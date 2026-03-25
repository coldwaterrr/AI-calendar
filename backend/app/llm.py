import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import litellm
from litellm import completion

from .schemas import EventCreate, ModelConfigTestRequest, ModelProvider


PROVIDER_PREFIXES: dict[ModelProvider, str] = {
    'openai': 'openai',
    'anthropic': 'anthropic',
    'gemini': 'gemini',
    'ollama': 'ollama',
    'custom': 'openai',
}

ENV_KEY_BY_PROVIDER: dict[ModelProvider, str] = {
    'openai': 'OPENAI_API_KEY',
    'anthropic': 'ANTHROPIC_API_KEY',
    'gemini': 'GEMINI_API_KEY',
    'ollama': 'OPENAI_API_KEY',
    'custom': 'OPENAI_API_KEY',
}

ENV_BASE_BY_PROVIDER: dict[ModelProvider, str] = {
    'openai': 'OPENAI_API_BASE',
    'anthropic': 'ANTHROPIC_API_BASE',
    'gemini': 'GEMINI_API_BASE',
    'ollama': 'OPENAI_API_BASE',
    'custom': 'OPENAI_API_BASE',
}

CATEGORY_COLORS = {
    'research': '#E45757',
    'meeting': '#4B7BE5',
    'life': '#3FAE6A',
}


@contextmanager
def temporary_env(var_map: dict[str, str | None]):
    previous = {key: os.environ.get(key) for key in var_map}
    try:
        for key, value in var_map.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def build_litellm_model_name(provider: ModelProvider, model: str) -> str:
    prefix = PROVIDER_PREFIXES[provider]
    return model if '/' in model else f'{prefix}/{model}'


def _env_values(provider: ModelProvider, api_key: str, base_url: str) -> dict[str, str | None]:
    return {
        ENV_KEY_BY_PROVIDER[provider]: api_key,
        ENV_BASE_BY_PROVIDER[provider]: base_url.strip() or None,
    }


def run_model_config_test(payload: ModelConfigTestRequest) -> tuple[bool, int, str]:
    if payload.provider in {'ollama', 'custom'} and not payload.base_url.strip():
        return False, 0, 'Base URL is required for ollama or custom providers.'

    started = time.perf_counter()
    try:
        with temporary_env(_env_values(payload.provider, payload.api_key, payload.base_url)):
            response = completion(
                model=build_litellm_model_name(payload.provider, payload.model),
                messages=[{'role': 'user', 'content': 'Reply with exactly: pong'}],
                api_base=payload.base_url.strip() or None,
                max_tokens=8,
                temperature=0,
            )
        latency_ms = int((time.perf_counter() - started) * 1000)
        content = response.choices[0].message.content if response.choices else 'OK'
        return True, latency_ms, f'Provider responded successfully: {content}'
    except litellm.AuthenticationError as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return False, latency_ms, f'Authentication failed: {exc}'
    except litellm.BadRequestError as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return False, latency_ms, f'Bad request: {exc}'
    except litellm.APIConnectionError as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return False, latency_ms, f'Connection failed: {exc}'
    except litellm.APIError as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return False, latency_ms, f'Provider API error: {exc}'
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return False, latency_ms, f'Unexpected error: {exc}'


def infer_event_with_llm(
    *,
    provider: ModelProvider,
    model: str,
    api_key: str,
    base_url: str,
    text: str,
) -> EventCreate:
    now = datetime.now(tz=timezone.utc)
    schema_hint = {
        'title': 'short event title',
        'description': 'details',
        'start_at': 'ISO8601 datetime',
        'end_at': 'ISO8601 datetime',
        'tense': 'past or future',
        'category': 'research or life or meeting',
        'confidence': 0.9,
    }
    prompt = (
        'Extract one calendar event from the user input. '
        'Return strict JSON only with keys: '
        f"{', '.join(schema_hint.keys())}. "
        f'Current time (UTC): {now.isoformat()}. '
        'Use ISO 8601 timestamps with timezone. '
        'If time is vague, infer a reasonable 1-hour duration. '
        'Choose tense from past/future and category from research/life/meeting. '
        f'User input: {text}'
    )

    with temporary_env(_env_values(provider, api_key, base_url)):
        response = completion(
            model=build_litellm_model_name(provider, model),
            messages=[{'role': 'user', 'content': prompt}],
            api_base=base_url.strip() or None,
            response_format={'type': 'json_object'},
            max_tokens=220,
            temperature=0,
        )

    raw_content = response.choices[0].message.content
    data = json.loads(raw_content)
    category = data['category']

    return EventCreate(
        id=f'evt_{uuid4().hex[:8]}',
        title=data['title'].strip() or text[:18] or 'Untitled event',
        description=data.get('description', '').strip(),
        start_at=datetime.fromisoformat(data['start_at']),
        end_at=datetime.fromisoformat(data['end_at']),
        tense=data['tense'],
        category=category,
        color=CATEGORY_COLORS[category],
        source_type='text',
        raw_input=text,
        confidence=float(data.get('confidence', 0.85)),
    )

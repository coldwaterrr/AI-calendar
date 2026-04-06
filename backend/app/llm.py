import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

import litellm
from litellm import completion

from .schemas import Event, EventCreate, ModelConfigTestRequest, ModelProvider


PROVIDER_PREFIXES: dict[ModelProvider, str] = {
    'openai': 'openai',
    'anthropic': 'anthropic',
    'gemini': 'gemini',
    'ollama': 'ollama',
    'openrouter': 'openrouter',
    'custom': 'openai',
}

ENV_KEY_BY_PROVIDER: dict[ModelProvider, str] = {
    'openai': 'OPENAI_API_KEY',
    'anthropic': 'ANTHROPIC_API_KEY',
    'gemini': 'GEMINI_API_KEY',
    'ollama': 'OPENAI_API_KEY',
    'openrouter': 'OPENROUTER_API_KEY',
    'custom': 'OPENAI_API_KEY',
}

ENV_BASE_BY_PROVIDER: dict[ModelProvider, str] = {
    'openai': 'OPENAI_API_BASE',
    'anthropic': 'ANTHROPIC_API_BASE',
    'gemini': 'GEMINI_API_BASE',
    'ollama': 'OPENAI_API_BASE',
    'openrouter': 'OPENROUTER_API_BASE',
    'custom': 'OPENAI_API_BASE',
}

CATEGORY_COLORS = {
    'research': '#E45757',
    'meeting': '#4B7BE5',
    'life': '#3FAE6A',
}


def _normalize_provider(provider: ModelProvider, base_url: str) -> ModelProvider:
    if provider == 'custom' and 'openrouter.ai' in base_url:
        return 'openrouter'
    return provider


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


def build_litellm_model_name(provider: ModelProvider, model: str, base_url: str = '') -> str:
    normalized_provider = _normalize_provider(provider, base_url)
    prefix = PROVIDER_PREFIXES[normalized_provider]
    if normalized_provider == 'openrouter' and model.startswith('openrouter/'):
        return model
    if normalized_provider != 'openrouter' and '/' in model:
        return model
    return f'{prefix}/{model}'


def _env_values(provider: ModelProvider, api_key: str, base_url: str) -> dict[str, str | None]:
    normalized_provider = _normalize_provider(provider, base_url)
    return {
        ENV_KEY_BY_PROVIDER[normalized_provider]: api_key,
        ENV_BASE_BY_PROVIDER[normalized_provider]: base_url.strip() or None,
    }


def run_model_config_test(payload: ModelConfigTestRequest) -> tuple[bool, int, str]:
    normalized_provider = _normalize_provider(payload.provider, payload.base_url)
    if normalized_provider in {'ollama', 'custom'} and not payload.base_url.strip():
        return False, 0, 'Base URL is required for ollama or custom providers.'

    started = time.perf_counter()
    try:
        with temporary_env(_env_values(payload.provider, payload.api_key, payload.base_url)):
            response = completion(
                model=build_litellm_model_name(payload.provider, payload.model, payload.base_url),
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
    prompt = (
        'Extract one calendar event from the user input. '
        'Return strict JSON only with keys: '
        'title, description, start_at, end_at, tense, category, confidence. '
        f'Current time (UTC): {now.isoformat()}. '
        'Use ISO 8601 timestamps with timezone. '
        'If time is vague, infer a reasonable 1-hour duration. '
        'Choose tense from past/future and category from research/life/meeting. '
        f'User input: {text}'
    )

    with temporary_env(_env_values(provider, api_key, base_url)):
        response = completion(
            model=build_litellm_model_name(provider, model, base_url),
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


def generate_summary(
    *,
    events: list[Event],
    days: int,
    provider: ModelProvider | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> tuple[str, str]:
    """Generate an AI summary of past events. Returns (summary_text, parser_mode)."""
    now = datetime.now(tz=timezone.utc)
    event_lines = []
    for e in events:
        start_str = e.start_at.strftime('%Y-%m-%d %H:%M')
        event_lines.append(
            f'- [{start_str}] {e.title} | {e.category} | {e.description}'
        )
    event_text = '\n'.join(event_lines) if event_lines else 'No events recorded.'

    now_str = now.strftime('%Y-%m-%d %H:%M')
    day_label = 'today' if days == 1 else f'the last {days} days'

    prompt = (
        f"今天是 {now_str}。用户在过去 {day_label} 的事件记录如下：\n\n{event_text}\n\n"
        "请用中文生成一段简洁的总结，涵盖用户在这段时间内的主要活动、投入的领域和大致节奏。"
        '要求 3-5 句话，语气自然友好，适合个人回顾。只返回总结文本，不要 JSON 或其他格式。'
    )

    if provider and model and api_key is not None:
        with temporary_env(
            _env_values(provider, api_key, base_url or '')
        ):
            response = completion(
                model=build_litellm_model_name(provider, model, base_url or ''),
                messages=[{'role': 'user', 'content': prompt}],
                api_base=(base_url or '').strip() or None,
                max_tokens=300,
                temperature=0.3,
            )
        summary = response.choices[0].message.content.strip() if response.choices else _fallback_summary(events, days)
        return summary, 'llm'
    else:
        return _fallback_summary(events, days), 'fallback'


def _fallback_summary(events: list[Event], days: int) -> str:
    if not events:
        return f'过去 {days} 天内暂无记录。试试用自然语言记录一下吧！'
    by_cat: dict[str, int] = {}
    for e in events:
        by_cat[e.category] = by_cat.get(e.category, 0) + 1
    parts = [f'过去 {days} 天共记录 {len(events)} 件事']
    cat_names = {'research': '研究开发', 'meeting': '会议', 'life': '生活'}
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        parts.append(f'{cat_names.get(cat, cat)} {count} 件')
    return '，'.join(parts) + '。'

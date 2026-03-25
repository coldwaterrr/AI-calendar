import os
import time
from contextlib import contextmanager

import litellm
from litellm import completion

from .schemas import ModelConfigTestRequest, ModelProvider


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


def run_model_config_test(payload: ModelConfigTestRequest) -> tuple[bool, int, str]:
    if payload.provider in {'ollama', 'custom'} and not payload.base_url.strip():
        return False, 0, 'Base URL is required for ollama or custom providers.'

    env_key = ENV_KEY_BY_PROVIDER[payload.provider]
    env_base = ENV_BASE_BY_PROVIDER[payload.provider]
    env_values = {
        env_key: payload.api_key,
        env_base: payload.base_url.strip() or None,
    }

    started = time.perf_counter()
    try:
        with temporary_env(env_values):
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

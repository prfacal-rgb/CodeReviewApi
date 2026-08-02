from functools import lru_cache

from core.config import settings
from core.providers.anthropic_provider import AnthropicProvider
from core.providers.base import BaseProvider
from core.providers.fallback_provider import FallbackProvider
from core.providers.openai_compatible_provider import OpenAICompatibleProvider


@lru_cache(maxsize=1)
def get_anthropic_provider() -> AnthropicProvider:
    return AnthropicProvider(api_key=settings.anthropic_api_key)


@lru_cache(maxsize=1)
def get_ollama_provider() -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        base_url=settings.ollama_base_url,
        api_key="ollama",
        provider_name="Ollama",
    )


@lru_cache(maxsize=1)
def get_groq_provider() -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        base_url=settings.groq_base_url,
        api_key=settings.groq_api_key,
        provider_name="Groq",
    )


@lru_cache(maxsize=1)
def get_google_provider() -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        base_url=settings.google_base_url,
        api_key=settings.google_api_key,
        provider_name="Google",
        vision=True,
    )


@lru_cache(maxsize=1)
def get_fallback_provider() -> FallbackProvider:
    return FallbackProvider(
        providers=[
            ("Groq", get_groq_provider(), "llama-3.3-70b-versatile"),
            ("Anthropic", get_anthropic_provider(), "claude-haiku-4-5-20251001"),
            ("Ollama", get_ollama_provider(), "qwen2.5-coder:14b"),
        ]
    )


def get_provider(provider_key: str) -> BaseProvider:
    """Devuelve el proveedor correcto según la clave del model registry."""
    match provider_key:
        case "anthropic":
            return get_anthropic_provider()
        case "ollama":
            return get_ollama_provider()
        case "groq":
            return get_groq_provider()
        case "google":
            return get_google_provider()
        case "fallback":
            return get_fallback_provider()
        case _:
            return get_ollama_provider()

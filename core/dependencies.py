import anthropic
from openai import OpenAI
from functools import lru_cache
from core.config import settings


@lru_cache
def get_anthropic_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


@lru_cache
def get_ollama_client() -> OpenAI:
    return OpenAI(
        base_url=settings.ollama_base_url,
        api_key="ollama",  # Ollama no valida esto, pero el SDK lo requiere
    )

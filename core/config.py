from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIProvider(str, Enum):
    anthropic = "anthropic"
    ollama = "ollama"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ← ignora variables del .env que no tengan campo en Settings
    )

    # Anthropic
    anthropic_api_key: str
    anthropic_model: str = "claude-haiku-4-5-20251001"

    # Ollama
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model_fast: str = "qwen2.5-coder:14b"
    ollama_model_deep: str = "qwen2.5-coder:32b"

    # General
    ai_provider: AIProvider = AIProvider.ollama
    app_env: str = "development"
    max_tokens: int = 2048


settings = Settings()  # type: ignore[call-arg]

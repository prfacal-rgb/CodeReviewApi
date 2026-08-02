from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Anthropic ─────────────────────────────────────────────────────────────
    anthropic_api_key: str = ""

    # ── Ollama (VM local) ─────────────────────────────────────────────────────
    ollama_base_url: str = "http://192.168.56.130:11434/v1"

    # ── Groq Cloud ────────────────────────────────────────────────────────────
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # ── Google AI Studio ──────────────────────────────────────────────────────
    google_api_key: str = ""
    google_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # ── General ───────────────────────────────────────────────────────────────
    max_tokens: int = 4096

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

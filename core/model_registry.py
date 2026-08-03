from pydantic import BaseModel


class ModelInfo(BaseModel):
    id: str  # identificador único que llega en cada request
    display_name: str  # texto que ve el usuario en el dropdown
    provider: str  # clave para el factory en dependencies.py
    model_name: str  # nombre real del modelo en la API del provider
    supports_vision: bool = False
    group: str = "cloud"  # "local" | "cloud" — para agrupar en el dropdown


MODELS: list[ModelInfo] = [
    # ── Local ─────────────────────────────────────────────────────────────────
    ModelInfo(
        id="ollama-fast",
        display_name="Ollama — qwen2.5-coder:14b (Rápido)",
        provider="ollama",
        model_name="qwen2.5-coder:14b",
        group="local",
    ),
    ModelInfo(
        id="ollama-deep",
        display_name="Ollama — qwen2.5-coder:32b (Profundo)",
        provider="ollama",
        model_name="qwen2.5-coder:32b",
        group="local",
    ),
    # ── Cloud ─────────────────────────────────────────────────────────────────
    ModelInfo(
        id="groq",
        display_name="Groq — Llama 3.3 70B",
        provider="groq",
        model_name="llama-3.3-70b-versatile",
        group="cloud",
    ),
    ModelInfo(
        id="anthropic-haiku",
        display_name="Anthropic — Claude Haiku",
        provider="anthropic",
        model_name="claude-haiku-4-5-20251001",
        supports_vision=True,
        group="cloud",
    ),
    ModelInfo(
        id="anthropic-sonnet",
        display_name="Anthropic — Claude Sonnet",
        provider="anthropic",
        model_name="claude-sonnet-4-6",
        supports_vision=True,
        group="cloud",
    ),
    ModelInfo(
        id="google-gemini-2.5-flash-lite",
        display_name="Google — Gemini 2.5 Flash Lite",
        provider="google",
        model_name="gemini-2.5-flash-lite",
        supports_vision=True,
        group="cloud",
    ),
    # Opción B: gemini-3.6-flash (el modelo más nuevo y recomendado en 2026)
    ModelInfo(
        id="google-gemini-3.6-flash",
        display_name="Google — Gemini 3.6 Flash",
        provider="google",
        model_name="gemini-3.6-flash",
        supports_vision=True,
        group="cloud",
    ),
    # ── Fallback híbrido ──────────────────────────────────────────────────────
    ModelInfo(
        id="fallback",
        display_name="Auto (Groq → Anthropic → Ollama)",
        provider="fallback",
        model_name="",  # cada sub-provider usa su propio model_name
        group="cloud",
    ),
]


def get_model(model_id: str) -> ModelInfo:
    """Busca un modelo por id. Devuelve ollama-fast como default si no existe."""
    found = next((m for m in MODELS if m.id == model_id), None)
    return found or MODELS[0]

import logging
from typing import Generator

from core.exceptions import AIProviderError
from core.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class FallbackProvider(BaseProvider):
    """
    Envuelve una lista ordenada de (nombre, provider, model_name) y los prueba
    en secuencia. Si uno falla con un error de dominio (auth, rate limit,
    unavailable), pasa automáticamente al siguiente.

    Ejemplo de cadena: groq → anthropic → ollama-fast

    Cada entrada lleva su propio model_name porque cada provider tiene
    nombres de modelos distintos (e.g. "llama-3.3-70b-versatile" en Groq
    vs "claude-haiku-4-5-20251001" en Anthropic).
    """

    def __init__(self, providers: list[tuple[str, BaseProvider, str]]) -> None:
        # (nombre_legible, provider, model_name)
        self.providers = providers

    # ── BaseProvider ──────────────────────────────────────────────────────────

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> str:
        last_error: Exception = RuntimeError(
            "FallbackProvider sin providers configurados"
        )
        for name, provider, model_name in self.providers:
            try:
                logger.info(f"Fallback: intentando '{name}' ({model_name})")
                result = provider.complete(system, user, model_name, max_tokens)
                logger.info(f"Fallback: '{name}' respondió OK")
                return result
            except AIProviderError as e:
                logger.warning(
                    f"Fallback: '{name}' falló ({type(e).__name__}: {e}) "
                    f"— probando siguiente..."
                )
                last_error = e
        raise last_error

    def stream(
        self, system: str, user: str, model: str, max_tokens: int
    ) -> Generator[str, None, None]:
        """
        Intenta cada provider hasta obtener el primer token.
        Una vez que el stream arrancó no se puede cambiar de provider.
        """
        last_error: Exception = RuntimeError(
            "FallbackProvider sin providers configurados"
        )
        for name, provider, model_name in self.providers:
            try:
                logger.info(f"Fallback stream: intentando '{name}' ({model_name})")
                gen = provider.stream(system, user, model_name, max_tokens)
                first = next(gen)  # si falla aquí → fallback
                logger.info(f"Fallback stream: '{name}' respondió OK")
                yield first
                yield from gen
                return
            except StopIteration:
                return  # stream vacío pero válido
            except AIProviderError as e:
                logger.warning(
                    f"Fallback stream: '{name}' falló "
                    f"({type(e).__name__}: {e}) — probando siguiente..."
                )
                last_error = e
        raise last_error

    def supports_vision(self) -> bool:
        return any(p.supports_vision() for _, p, _ in self.providers)

    def complete_with_image(
        self,
        system: str,
        image_base64: str,
        mime_type: str,
        model: str,
        max_tokens: int,
    ) -> str:
        last_error: Exception = RuntimeError("No hay providers con visión configurados")
        for name, provider, model_name in self.providers:
            if not provider.supports_vision():
                continue
            try:
                logger.info(f"Fallback vision: intentando '{name}'")
                return provider.complete_with_image(
                    system, image_base64, mime_type, model_name, max_tokens
                )
            except AIProviderError as e:
                logger.warning(
                    f"Fallback vision: '{name}' falló "
                    f"({type(e).__name__}: {e}) — probando siguiente..."
                )
                last_error = e
        raise last_error

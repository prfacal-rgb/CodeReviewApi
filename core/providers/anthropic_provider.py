import logging
from typing import Any, Generator

import anthropic
from anthropic.types import TextBlock

from core.exceptions import (
    AIAuthenticationError,
    AIRateLimitError,
    AIUnavailableError,
)
from core.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """Proveedor para la API de Anthropic (Claude). Soporta visión."""

    def __init__(self, api_key: str) -> None:
        self.client = anthropic.Anthropic(api_key=api_key)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _handle_error(self, exc: Exception) -> None:
        if isinstance(exc, anthropic.AuthenticationError):
            raise AIAuthenticationError(
                "Anthropic API key inválida — revisá ANTHROPIC_API_KEY en .env"
            )
        if isinstance(exc, anthropic.RateLimitError):
            raise AIRateLimitError(
                "Rate limit de Anthropic alcanzado — intentá más tarde"
            )
        if isinstance(exc, anthropic.APIConnectionError):
            raise AIUnavailableError("No se puede conectar con la API de Anthropic")
        raise exc

    def _extract_text(self, message: anthropic.types.Message) -> str:
        block = next(b for b in message.content if isinstance(b, TextBlock))
        return block.text

    # ── BaseProvider ──────────────────────────────────────────────────────────

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> str:
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return self._extract_text(message)
        except Exception as e:
            self._handle_error(e)
            return ""  # inalcanzable — satisface al type checker

    def stream(
        self, system: str, user: str, model: str, max_tokens: int
    ) -> Generator[str, None, None]:
        try:
            with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            ) as s:
                yield from s.text_stream
        except Exception as e:
            self._handle_error(e)

    def supports_vision(self) -> bool:
        return True

    def complete_with_image(
        self,
        system: str,
        image_base64: str,
        mime_type: str,
        model: str,
        max_tokens: int,
    ) -> str:
        img_messages: Any = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Extract the code from this image and review it. "
                            "Respond with the JSON structure specified."
                        ),
                    },
                ],
            }
        ]
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=img_messages,
            )
            return self._extract_text(message)
        except Exception as e:
            self._handle_error(e)
            return ""

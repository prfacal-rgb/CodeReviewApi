import logging
from typing import Any, Generator

import openai
from openai import OpenAI

from core.exceptions import (
    AIAuthenticationError,
    AIRateLimitError,
    AIUnavailableError,
)
from core.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(BaseProvider):
    """
    Proveedor para APIs compatibles con OpenAI.

    Un solo código sirve para tres proveedores distintos — solo cambia
    base_url y api_key:
      • Ollama  → base_url=http://host:11434/v1  api_key="ollama"
      • Groq    → base_url=https://api.groq.com/openai/v1  api_key=GROQ_API_KEY
      • Google  → base_url=https://generativelanguage.googleapis.com/v1beta/openai/
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        provider_name: str,
        vision: bool = False,
    ) -> None:
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.provider_name = provider_name
        self._vision = vision

    # ── helpers ───────────────────────────────────────────────────────────────

    def _handle_error(self, exc: Exception) -> None:
        if isinstance(exc, openai.AuthenticationError):
            raise AIAuthenticationError(f"API key inválida para {self.provider_name}")
        if isinstance(exc, openai.RateLimitError):
            raise AIRateLimitError(f"Rate limit alcanzado en {self.provider_name}")
        if isinstance(exc, openai.APIConnectionError):
            raise AIUnavailableError(f"No se puede conectar con {self.provider_name}")
        raise exc

    # ── BaseProvider ──────────────────────────────────────────────────────────

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            self._handle_error(e)
            return ""

    def stream(
        self, system: str, user: str, model: str, max_tokens: int
    ) -> Generator[str, None, None]:
        try:
            response = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                stream=True,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            self._handle_error(e)

    def supports_vision(self) -> bool:
        return self._vision

    def complete_with_image(
        self,
        system: str,
        image_base64: str,
        mime_type: str,
        model: str,
        max_tokens: int,
    ) -> str:
        # Formato image_url — compatible con Ollama llava y Google
        img_messages: Any = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
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
            completion = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=img_messages,
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            self._handle_error(e)
            return ""

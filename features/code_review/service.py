import json
import re
from typing import Generator

from core.config import settings
from core.exceptions import AIUnavailableError
from core.providers.base import BaseProvider
from features.code_review.models import (
    ImageReviewRequest,
    ReviewResponse,
    SuggestionItem,
)
from features.code_review.prompts import SYSTEM_PROMPT, build_user_prompt


def _extract_json(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()


class CodeReviewService:
    def __init__(self, provider: BaseProvider) -> None:
        self.provider = provider

    # ── Revisión síncrona ─────────────────────────────────────────────────────

    def review(self, code: str, language: str, model_name: str) -> ReviewResponse:
        raw = self.provider.complete(
            system=SYSTEM_PROMPT,
            user=build_user_prompt(code, language, None),
            model=model_name,
            max_tokens=settings.max_tokens,
        )
        return self._parse(raw)

    # ── Revisión con streaming ────────────────────────────────────────────────

    def review_stream(
        self, code: str, language: str, model_name: str
    ) -> Generator[str, None, None]:
        yield from self.provider.stream(
            system=SYSTEM_PROMPT,
            user=build_user_prompt(code, language, None),
            model=model_name,
            max_tokens=settings.max_tokens,
        )

    # ── Revisión desde imagen ─────────────────────────────────────────────────

    def review_from_image(
        self, request: ImageReviewRequest, model_name: str
    ) -> ReviewResponse:
        if not self.provider.supports_vision():
            raise AIUnavailableError(
                "El proveedor seleccionado no soporta análisis de imágenes. "
                "Usá Anthropic (claude-haiku) o Google (gemini-2.5-flash)."
            )
        raw = self.provider.complete_with_image(
            system=SYSTEM_PROMPT,
            image_base64=request.image_base64,
            mime_type=request.mime_type,
            model=model_name,
            max_tokens=settings.max_tokens,
        )
        return self._parse(raw)

    # ── Parser ────────────────────────────────────────────────────────────────

    def _parse(self, raw: str) -> ReviewResponse:
        data = json.loads(_extract_json(raw))
        suggestions = [
            SuggestionItem(
                severity=s.get("severity", "info"),
                category=s.get("category", ""),
                description=s.get("description", ""),
                how_to_fix=s.get("how_to_fix", ""),
                example_fix=s.get("example_fix", ""),
            )
            for s in data.get("suggestions", [])
        ]
        return ReviewResponse(
            overall_score=data.get("overall_score", 5),
            language_detected=data.get("language_detected", "unknown"),
            summary=data.get("summary", ""),
            suggestions=suggestions,
            refactored_code=data.get("refactored_code", ""),
        )

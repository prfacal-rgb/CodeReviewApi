import json
import re

from core.config import settings
from core.providers.base import BaseProvider
from features.explain.models import ExplainRequest, ExplainResponse
from features.explain.prompts import SYSTEM_PROMPT, build_prompt


def _extract_json(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()


class ExplainService:
    def __init__(self, provider: BaseProvider) -> None:
        self.provider = provider

    def explain(self, request: ExplainRequest, model_name: str) -> ExplainResponse:
        raw = self.provider.complete(
            system=SYSTEM_PROMPT,
            user=build_prompt(
                request.suggestion, request.original_code, request.language
            ),
            model=model_name,
            max_tokens=settings.max_tokens,
        )
        data = json.loads(_extract_json(raw))
        return ExplainResponse(
            why_it_matters=data.get("why_it_matters", ""),
            detailed_explanation=data.get("detailed_explanation", ""),
            example_fix=data.get("example_fix", ""),
            references=data.get("references", []),
        )

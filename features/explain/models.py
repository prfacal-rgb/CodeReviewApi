from pydantic import BaseModel, Field
from features.code_review.models import SuggestionItem


class ExplainRequest(BaseModel):
    original_code: str = Field(..., min_length=10)
    language: str = "auto"  # ← este campo faltaba
    suggestion: SuggestionItem  # ← objeto completo, no string
    model_id: str = "ollama-fast"  # antes era deep: bool


class ExplainResponse(BaseModel):
    why_it_matters: str
    detailed_explanation: str
    example_fix: str
    references: list[str]

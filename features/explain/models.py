from pydantic import BaseModel, Field
from features.code_review.models import Suggestion


class ExplainRequest(BaseModel):
    suggestion: Suggestion
    original_code: str = Field(..., min_length=10)
    language: str = "python"
    deep: bool = False


class ExplainResponse(BaseModel):
    why_it_matters: str
    detailed_explanation: str
    example_fix: str
    references: list[str]

from pydantic import BaseModel, Field
from enum import Enum


class Language(str, Enum):
    python = "python"
    javascript = "javascript"
    csharp = "csharp"
    auto = "auto"  # el modelo detecta el lenguaje


class ReviewRequest(BaseModel):
    code: str = Field(..., min_length=10, description="Código a revisar")
    language: Language = Language.auto
    context: str | None = Field(None, description="Contexto opcional del código")
    deep: bool = Field(
        False,
        description="False = respuesta rápida (14b) | True = análisis profundo (32b)",
    )


class Suggestion(BaseModel):
    severity: str  # "info" | "warning" | "critical"
    category: str  # "performance" | "security" | "readability" | "bug"
    description: str
    line_hint: str | None = None


class ReviewResponse(BaseModel):
    language_detected: str
    summary: str
    suggestions: list[Suggestion]
    refactored_code: str
    overall_score: int  # 1-10

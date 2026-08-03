from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    code: str = Field(..., min_length=10)
    language: str = "auto"
    model_id: str = "ollama-fast"  # antes era deep: bool


class ImageReviewRequest(BaseModel):
    image_base64: str
    mime_type: str = "image/png"
    model_id: str = "anthropic"  # default a Anthropic porque vision


class SuggestionItem(BaseModel):
    severity: str
    category: str
    description: str
    how_to_fix: str = ""  # ← default vacío, no 422 si el AI no lo devuelve
    example_fix: str = ""  # ← ídem


class ReviewResponse(BaseModel):
    overall_score: int
    language_detected: str
    summary: str
    suggestions: list[SuggestionItem]
    refactored_code: str

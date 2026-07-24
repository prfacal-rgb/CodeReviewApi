# from typing import Union

# import anthropic
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

# from openai import OpenAI

from core.config import settings, AIProvider
from core.dependencies import get_anthropic_client, get_ollama_client
from features.code_review.models import ReviewRequest, ReviewResponse
from features.code_review.service import CodeReviewService

router = APIRouter(prefix="/reviews", tags=["Code Review"])


def get_review_service() -> CodeReviewService:
    """Única función que decide qué cliente y provider usar."""
    if settings.ai_provider == AIProvider.anthropic:
        return CodeReviewService(get_anthropic_client(), AIProvider.anthropic)
    return CodeReviewService(get_ollama_client(), AIProvider.ollama)


@router.post("", response_model=ReviewResponse)
def create_review(
    request: ReviewRequest, service: CodeReviewService = Depends(get_review_service)
) -> ReviewResponse:
    return service.review(request)


@router.post("/stream")
def create_review_stream(
    request: ReviewRequest, service: CodeReviewService = Depends(get_review_service)
) -> StreamingResponse:
    return StreamingResponse(service.review_stream(request), media_type="text/plain")

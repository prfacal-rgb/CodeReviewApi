from fastapi import APIRouter, Depends

from core.config import settings, AIProvider
from core.dependencies import get_anthropic_client, get_ollama_client
from features.explain.models import ExplainRequest, ExplainResponse
from features.explain.service import ExplainService

router = APIRouter(prefix="/explain", tags=["Explain"])


def get_explain_service() -> ExplainService:
    if settings.ai_provider == AIProvider.anthropic:
        return ExplainService(get_anthropic_client(), AIProvider.anthropic)
    return ExplainService(get_ollama_client(), AIProvider.ollama)


@router.post("", response_model=ExplainResponse)
def explain_suggestion(
    request: ExplainRequest, service: ExplainService = Depends(get_explain_service)
) -> ExplainResponse:
    return service.explain(request)

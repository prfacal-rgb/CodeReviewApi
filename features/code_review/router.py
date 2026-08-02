from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from core.dependencies import get_provider
from core.exceptions import AIAuthenticationError, AIProviderError, AIUnavailableError
from core.model_registry import MODELS, get_model
from features.code_review.models import (
    ImageReviewRequest,
    ReviewRequest,
    ReviewResponse,
)
from features.code_review.service import CodeReviewService

router = APIRouter(prefix="/reviews", tags=["code-review"])


# ── Dependency (overrideable en tests) ────────────────────────────────────────


async def get_review_service(request: Request) -> CodeReviewService:
    """
    Lee model_id del body y devuelve el servicio con el proveedor correcto.
    En tests se sobreescribe vía app.dependency_overrides[get_review_service].
    """
    body = await request.json()
    model_id = body.get("model_id", "ollama-fast")
    model_info = get_model(model_id)
    return CodeReviewService(get_provider(model_info.provider))


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/models")
def list_models() -> list[dict]:
    """Lista de modelos disponibles para el dropdown del frontend."""
    return [m.model_dump() for m in MODELS]


@router.post("", response_model=ReviewResponse)
def create_review(
    req: ReviewRequest,
    service: CodeReviewService = Depends(get_review_service),
):
    try:
        model_info = get_model(req.model_id)
        return service.review(req.code, req.language, model_info.model_name)
    except AIAuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except AIUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/stream")
def stream_review(
    req: ReviewRequest,
    service: CodeReviewService = Depends(get_review_service),
):
    model_info = get_model(req.model_id)

    def generate():
        try:
            yield from service.review_stream(
                req.code, req.language, model_info.model_name
            )
        except GeneratorExit:
            pass
        except AIAuthenticationError as e:
            yield f"\n[ERROR_AUTH] {e}"
        except AIUnavailableError as e:
            yield f"\n[ERROR_UNAVAILABLE] {e}"
        except AIProviderError as e:
            yield f"\n[ERROR] {e}"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/image", response_model=ReviewResponse)
def review_from_image(
    req: ImageReviewRequest,
    service: CodeReviewService = Depends(get_review_service),
):
    try:
        model_info = get_model(req.model_id)
        return service.review_from_image(req, model_info.model_name)
    except AIAuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except AIUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))

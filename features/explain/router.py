from fastapi import APIRouter, Depends, HTTPException, Request

from core.dependencies import get_provider
from core.exceptions import AIAuthenticationError, AIProviderError, AIUnavailableError
from core.model_registry import get_model
from features.explain.models import ExplainRequest, ExplainResponse
from features.explain.service import ExplainService

router = APIRouter(prefix="/explain", tags=["explain"])


# ── Dependency (overrideable en tests) ────────────────────────────────────────


async def get_explain_service(request: Request) -> ExplainService:
    """
    Lee model_id del body y devuelve el servicio con el proveedor correcto.
    En tests se sobreescribe vía app.dependency_overrides[get_explain_service].
    """
    body = await request.json()
    model_id = body.get("model_id", "ollama-fast")
    model_info = get_model(model_id)
    return ExplainService(get_provider(model_info.provider))


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("", response_model=ExplainResponse)
def explain(
    req: ExplainRequest,
    service: ExplainService = Depends(get_explain_service),
):
    try:
        model_info = get_model(req.model_id)
        return service.explain(req, model_info.model_name)
    except AIAuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except AIUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))

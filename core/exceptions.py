import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


# ── Excepciones de dominio ─────────────────────────────────────────
class AIProviderError(Exception):
    """Base para errores del proveedor de IA."""

    pass


class AIAuthenticationError(AIProviderError):
    """API key inválida o no autorizado."""

    pass


class AIRateLimitError(AIProviderError):
    """Rate limit excedido."""

    pass


class AIUnavailableError(AIProviderError):
    """Proveedor inaccesible o caído."""

    pass


# ── HTTP Handlers ──────────────────────────────────────────────────


async def ai_auth_handler(request: Request, exc: AIAuthenticationError) -> JSONResponse:
    logger.warning(f"Authentication error: {exc}")
    return JSONResponse(
        status_code=401, content={"error": "authentication_error", "detail": str(exc)}
    )


async def ai_rate_limit_handler(
    request: Request, exc: AIRateLimitError
) -> JSONResponse:
    logger.warning(f"Rate limit hit: {exc}")
    return JSONResponse(
        status_code=429, content={"error": "rate_limit_error", "detail": str(exc)}
    )


async def ai_unavailable_handler(
    request: Request, exc: AIUnavailableError
) -> JSONResponse:
    logger.error(f"Provider unavailable: {exc}")
    return JSONResponse(
        status_code=503, content={"error": "provider_unavailable", "detail": str(exc)}
    )


async def validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {
            "field": " → ".join(str(loc) for loc in err["loc"] if loc != "body"),
            "message": err["msg"],
            "type": err["type"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": "Invalid request body",
            "errors": errors,
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled error on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500, content={"error": "internal_error", "detail": str(exc)}
    )

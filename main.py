from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from core.logging_config import setup_logging
from core.exceptions import (
    AIAuthenticationError,
    AIRateLimitError,
    AIUnavailableError,
    ai_auth_handler,
    ai_rate_limit_handler,
    ai_unavailable_handler,
    validation_handler,
    global_exception_handler,
)
from features.code_review.router import router as review_router
from features.explain.router import router as explain_router  # ← nuevo

setup_logging()

app = FastAPI(title="Code Review API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handlers en orden de especificidad — los más específicos primero
app.add_exception_handler(AIAuthenticationError, ai_auth_handler)  # type: ignore[arg-type] # noqa: E501
app.add_exception_handler(AIRateLimitError, ai_rate_limit_handler)  # type: ignore[arg-type] # noqa: E501
app.add_exception_handler(AIUnavailableError, ai_unavailable_handler)  # type: ignore[arg-type] # noqa: E501
app.add_exception_handler(RequestValidationError, validation_handler)  # type: ignore[arg-type] # noqa: E501
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(review_router)
app.include_router(explain_router)


@app.get("/health")
def health():
    return {"status": "ok"}

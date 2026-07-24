import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from main import app
from core.config import AIProvider
from features.code_review.router import get_review_service
from features.code_review.service import CodeReviewService

MOCK_REVIEW = {
    "language_detected": "python",
    "summary": "Function has edge case issues.",
    "suggestions": [
        {
            "severity": "warning",
            "category": "bug",
            "description": "Division by zero when list is empty.",
            "line_hint": "return line",
        }
    ],
    "refactored_code": (
        "def avg(nums):\n"
        "if not nums:\n"
        "raise ValueError\n"
        "return sum(nums)/len(nums)"
    ),
    "overall_score": 6,
}


# ── Clientes mock ──────────────────────────────────────────────────
@pytest.fixture
def mock_ollama_client():
    client = MagicMock()
    response = MagicMock()
    response.choices[0].message.content = json.dumps(MOCK_REVIEW)
    client.chat.completions.create.return_value = response
    return client


@pytest.fixture
def mock_anthropic_client():
    from anthropic.types import TextBlock  # ← import real TextBlock

    client = MagicMock()
    text_block = TextBlock(type="text", text=json.dumps(MOCK_REVIEW))  # ← objeto real
    message = MagicMock()
    message.content = [text_block]
    client.messages.create.return_value = message
    return client


# ── Services mock (usan los clientes de arriba) ───────────────────
@pytest.fixture
def mock_ollama_service(mock_ollama_client):
    return CodeReviewService(mock_ollama_client, AIProvider.ollama)


@pytest.fixture
def mock_anthropic_service(mock_anthropic_client):
    return CodeReviewService(mock_anthropic_client, AIProvider.anthropic)


# ── TestClient con dependencia reemplazada ────────────────────────
@pytest.fixture
def api_client(mock_ollama_service):
    app.dependency_overrides[get_review_service] = lambda: mock_ollama_service
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()

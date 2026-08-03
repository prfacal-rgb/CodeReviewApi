import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from main import app
from core.providers.base import BaseProvider
from features.code_review.router import get_review_service
from features.code_review.service import CodeReviewService

# ── Datos mock ────────────────────────────────────────────────────────────────

MOCK_REVIEW = {
    "language_detected": "python",
    "summary": "Function has edge case issues.",
    "suggestions": [
        {
            "severity": "warning",
            "category": "bug",
            "description": "Division by zero when list is empty.",
            "how_to_fix": "Check if nums is empty before dividing.",
            "example_fix": "if not nums:\n    raise ValueError('Empty list')",
        }
    ],
    "refactored_code": (
        "def avg(nums):\n"
        "    if not nums:\n"
        "        raise ValueError\n"
        "    return sum(nums) / len(nums)"
    ),
    "overall_score": 6,
}

MOCK_EXPLAIN = {
    "why_it_matters": "Division by zero causes unhandled exceptions in production.",
    "detailed_explanation": "When nums is empty, len(nums) returns 0 and the division "
    "fails.",
    "example_fix": "if not nums:\n    raise ValueError('Empty list')",
    "references": ["PEP 20", "Python docs: exceptions"],
}

# ── Provider mock (reemplaza los client mocks de Anthropic/OpenAI) ────────────


@pytest.fixture
def mock_provider():
    provider = MagicMock(spec=BaseProvider)
    provider.complete.return_value = json.dumps(MOCK_REVIEW)
    provider.stream.return_value = iter([json.dumps(MOCK_REVIEW)])
    provider.supports_vision.return_value = True
    provider.complete_with_image.return_value = json.dumps(MOCK_REVIEW)
    return provider


# ── Services mock ─────────────────────────────────────────────────────────────


@pytest.fixture
def mock_review_service(mock_provider):
    return CodeReviewService(mock_provider)


# ── TestClient con dependencia reemplazada ────────────────────────────────────


@pytest.fixture
def api_client(mock_review_service):
    app.dependency_overrides[get_review_service] = lambda: mock_review_service
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()

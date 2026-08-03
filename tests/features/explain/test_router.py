import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from main import app
from core.providers.base import BaseProvider
from features.explain.router import get_explain_service
from features.explain.service import ExplainService

MOCK_EXPLAIN = {
    "why_it_matters": "Division by zero causes unhandled exceptions.",
    "detailed_explanation": "When nums is empty, the division fails.",
    "example_fix": "if not nums:\n    raise ValueError('Empty list')",
    "references": ["PEP 20"],
}

VALID_CODE = "def calcular_promedio(n):\n    return sum(n)/len(n)"

VALID_SUGGESTION = {
    "severity": "warning",
    "category": "bug",
    "description": "Division by zero when list is empty.",
    "how_to_fix": "Check if nums is empty before dividing.",
    "example_fix": "if not nums:\n    raise ValueError('Empty list')",
}


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_explain_service():
    provider = MagicMock(spec=BaseProvider)
    provider.complete.return_value = json.dumps(MOCK_EXPLAIN)
    return ExplainService(provider)


@pytest.fixture
def api_client(mock_explain_service):
    # Override local — no pisa el api_client del conftest (que es del code_review)
    app.dependency_overrides[get_explain_service] = lambda: mock_explain_service
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


# ── POST /explain ─────────────────────────────────────────────────────────────


def test_explain_success(api_client):
    response = api_client.post(
        "/explain",
        json={
            "original_code": VALID_CODE,
            "language": "python",
            "suggestion": VALID_SUGGESTION,
            "model_id": "ollama-fast",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "why_it_matters" in data
    assert "detailed_explanation" in data
    assert "example_fix" in data
    assert isinstance(data["references"], list)


def test_explain_default_model_id(api_client):
    # Sin model_id → default "ollama-fast", no debe dar error
    response = api_client.post(
        "/explain",
        json={"original_code": VALID_CODE, "suggestion": VALID_SUGGESTION},
    )
    assert response.status_code == 200


def test_explain_rejects_short_code(api_client):
    assert (
        api_client.post(
            "/explain",
            json={"original_code": "x = 1", "suggestion": VALID_SUGGESTION},
        ).status_code
        == 422
    )


def test_explain_rejects_missing_suggestion(api_client):
    assert (
        api_client.post(
            "/explain",
            json={"original_code": VALID_CODE},
        ).status_code
        == 422
    )


def test_explain_rejects_missing_code(api_client):
    assert (
        api_client.post(
            "/explain",
            json={"suggestion": VALID_SUGGESTION},
        ).status_code
        == 422
    )

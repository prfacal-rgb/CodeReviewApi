import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from main import app
from features.explain.router import get_explain_service
from features.explain.service import ExplainService
from features.explain.models import ExplainResponse

MOCK_EXPLAIN = {
    "why_it_matters": "Excessive casts make the code harder to maintain.",
    "detailed_explanation": "cast() tells the type checker to treat a value as a "
    "different type.",
    "example_fix": "assert isinstance(client, anthropic.Anthropic)",
    "references": ["PEP 484"],
}

VALID_SUGGESTION = {
    "severity": "warning",
    "category": "readability",
    "description": "Excessive use of casts.",
    "line_hint": "_call_anthropic",
}

VALID_CODE = "def foo():\n    return cast(int, value)"


@pytest.fixture
def mock_explain_service():
    service = MagicMock(spec=ExplainService)
    service.explain.return_value = ExplainResponse(**MOCK_EXPLAIN)
    return service


# Fixture local — sobreescribe el api_client del conftest para inyectar el explain
# service
@pytest.fixture
def api_client(mock_explain_service):
    app.dependency_overrides[get_explain_service] = lambda: mock_explain_service
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


class TestExplainRouter:
    def test_explain_success(self, api_client):
        res = api_client.post(
            "/explain",
            json={
                "suggestion": VALID_SUGGESTION,
                "original_code": VALID_CODE,
                "language": "python",
                "deep": False,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["why_it_matters"] == MOCK_EXPLAIN["why_it_matters"]
        assert data["example_fix"] == MOCK_EXPLAIN["example_fix"]
        assert data["references"] == MOCK_EXPLAIN["references"]

    def test_explain_rejects_short_code(self, api_client):
        res = api_client.post(
            "/explain",
            json={
                "suggestion": VALID_SUGGESTION,
                "original_code": "x = 1",  # menos de 10 chars
                "language": "python",
            },
        )
        assert res.status_code == 422
        assert res.json()["error"] == "validation_error"

    def test_explain_rejects_missing_suggestion(self, api_client):
        res = api_client.post(
            "/explain", json={"original_code": VALID_CODE, "language": "python"}
        )
        assert res.status_code == 422

    def test_explain_uses_service(self, api_client, mock_explain_service):
        api_client.post(
            "/explain",
            json={
                "suggestion": VALID_SUGGESTION,
                "original_code": VALID_CODE,
                "language": "python",
                "deep": False,
            },
        )
        mock_explain_service.explain.assert_called_once()

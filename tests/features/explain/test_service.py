import json
import pytest
from unittest.mock import MagicMock

from core.exceptions import AIAuthenticationError, AIUnavailableError
from core.providers.base import BaseProvider
from features.explain.models import ExplainRequest, ExplainResponse
from features.explain.service import ExplainService, _extract_json
from features.code_review.models import SuggestionItem

MOCK_EXPLAIN = {
    "why_it_matters": "Division by zero causes unhandled exceptions in production.",
    "detailed_explanation": "When nums is empty, len(nums) returns 0 and the division "
    "fails.",
    "example_fix": "if not nums:\n    raise ValueError('Empty list')",
    "references": ["PEP 20", "Python docs: exceptions"],
}

MOCK_SUGGESTION = SuggestionItem(
    severity="warning",
    category="bug",
    description="Division by zero when list is empty.",
    how_to_fix="Check if nums is empty before dividing.",
    example_fix="if not nums:\n    raise ValueError('Empty list')",
)

VALID_CODE = "def calcular_promedio(n):\n    return sum(n)/len(n)"
MODEL = "qwen2.5-coder:14b"


# ── _extract_json ─────────────────────────────────────────────────────────────


def test_extract_json_plain():
    assert _extract_json('{"key": "value"}') == '{"key": "value"}'


def test_extract_json_strips_markdown_fences():
    assert _extract_json('```json\n{"key": "value"}\n```') == '{"key": "value"}'


def test_extract_json_strips_fences_without_language():
    assert _extract_json('```\n{"key": "value"}\n```') == '{"key": "value"}'


# ── Fixtures locales ──────────────────────────────────────────────────────────


@pytest.fixture
def provider():
    p = MagicMock(spec=BaseProvider)
    p.complete.return_value = json.dumps(MOCK_EXPLAIN)
    return p


@pytest.fixture
def service(provider):
    return ExplainService(provider)


@pytest.fixture
def req():
    return ExplainRequest(
        original_code=VALID_CODE,
        language="python",
        suggestion=MOCK_SUGGESTION,
    )


# ── ExplainService.explain() ──────────────────────────────────────────────────


def test_explain_returns_response(service, req):
    result = service.explain(req, MODEL)
    assert isinstance(result, ExplainResponse)
    assert result.why_it_matters == MOCK_EXPLAIN["why_it_matters"]
    assert result.references == MOCK_EXPLAIN["references"]


def test_explain_calls_provider_complete(provider, service, req):
    service.explain(req, MODEL)
    provider.complete.assert_called_once()


def test_explain_passes_model_name_to_provider(provider, service, req):
    service.explain(req, MODEL)
    assert provider.complete.call_args.kwargs["model"] == MODEL


def test_explain_propagates_auth_error(provider, service, req):
    provider.complete.side_effect = AIAuthenticationError("bad key")
    with pytest.raises(AIAuthenticationError):
        service.explain(req, MODEL)


def test_explain_propagates_unavailable_error(provider, service, req):
    provider.complete.side_effect = AIUnavailableError("no connection")
    with pytest.raises(AIUnavailableError):
        service.explain(req, MODEL)

import json
import pytest
from unittest.mock import MagicMock

import anthropic
import openai
from anthropic.types import TextBlock

from core.config import AIProvider
from core.exceptions import AIAuthenticationError, AIRateLimitError, AIUnavailableError
from features.code_review.models import Suggestion
from features.explain.models import ExplainRequest, ExplainResponse
from features.explain.service import ExplainService, _extract_json

MOCK_EXPLAIN = {
    "why_it_matters": "Excessive casts make the code harder to maintain.",
    "detailed_explanation": "cast() tells the type checker to treat a value as a "
    "different type without runtime checks.",
    "example_fix": "assert isinstance(client, anthropic.Anthropic), "
    "'Wrong client type'",
    "references": ["PEP 484 -- Type Hints", "Python isinstance() in Practice"],
}

MOCK_SUGGESTION = Suggestion(
    severity="warning",
    category="readability",
    description="Excessive use of casts.",
    line_hint="_call_anthropic",
)

VALID_CODE = "def foo():\n    return cast(int, value)"


# ── _extract_json ─────────────────────────────────────────────────────────────


class TestExtractJson:
    def test_returns_plain_json_unchanged(self):
        text = '{"key": "value"}'
        assert _extract_json(text) == text

    def test_strips_json_markdown_fence(self):
        text = '```json\n{"key": "value"}\n```'
        assert _extract_json(text) == '{"key": "value"}'

    def test_strips_plain_markdown_fence(self):
        text = '```\n{"key": "value"}\n```'
        assert _extract_json(text) == '{"key": "value"}'


# ── Ollama ────────────────────────────────────────────────────────────────────


class TestExplainServiceOllama:
    @pytest.fixture
    def ollama_client(self):
        client = MagicMock()
        response = MagicMock()
        response.choices[0].message.content = json.dumps(MOCK_EXPLAIN)
        client.chat.completions.create.return_value = response
        return client

    @pytest.fixture
    def service(self, ollama_client):
        return ExplainService(ollama_client, AIProvider.ollama)

    def test_is_not_anthropic(self, service):
        assert service.is_anthropic is False

    def test_uses_fast_model_by_default(self, service, ollama_client):
        from core.config import settings

        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        service.explain(req)
        call_kwargs = ollama_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == settings.ollama_model_fast

    def test_uses_deep_model_when_requested(self, service, ollama_client):
        from core.config import settings

        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=True,
        )
        service.explain(req)
        call_kwargs = ollama_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == settings.ollama_model_deep

    def test_calls_ollama_completions(self, service, ollama_client):
        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        service.explain(req)
        ollama_client.chat.completions.create.assert_called_once()

    def test_returns_explain_response(self, service):
        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        result = service.explain(req)
        assert isinstance(result, ExplainResponse)
        assert result.why_it_matters == MOCK_EXPLAIN["why_it_matters"]
        assert result.example_fix == MOCK_EXPLAIN["example_fix"]
        assert result.references == MOCK_EXPLAIN["references"]

    def test_auth_error_raises_domain_exception(self, service, ollama_client):
        ollama_client.chat.completions.create.side_effect = openai.AuthenticationError(
            message="Unauthorized", response=MagicMock(), body=None
        )
        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        with pytest.raises(AIAuthenticationError):
            service.explain(req)

    def test_connection_error_raises_domain_exception(self, service, ollama_client):
        ollama_client.chat.completions.create.side_effect = openai.APIConnectionError(
            request=MagicMock()
        )
        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        with pytest.raises(AIUnavailableError):
            service.explain(req)

    def test_rate_limit_raises_domain_exception(self, service, ollama_client):
        ollama_client.chat.completions.create.side_effect = openai.RateLimitError(
            message="Rate limit", response=MagicMock(), body=None
        )
        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        with pytest.raises(AIRateLimitError):
            service.explain(req)


# ── Anthropic ─────────────────────────────────────────────────────────────────


class TestExplainServiceAnthropic:
    @pytest.fixture
    def anthropic_client(self):
        client = MagicMock()
        text_block = TextBlock(type="text", text=json.dumps(MOCK_EXPLAIN))
        message = MagicMock()
        message.content = [text_block]
        client.messages.create.return_value = message
        return client

    @pytest.fixture
    def service(self, anthropic_client):
        return ExplainService(anthropic_client, AIProvider.anthropic)

    def test_is_anthropic(self, service):
        assert service.is_anthropic is True

    def test_calls_anthropic_messages(self, service, anthropic_client):
        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        service.explain(req)
        anthropic_client.messages.create.assert_called_once()

    def test_returns_explain_response(self, service):
        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        result = service.explain(req)
        assert isinstance(result, ExplainResponse)
        assert result.detailed_explanation == MOCK_EXPLAIN["detailed_explanation"]

    def test_auth_error_raises_domain_exception(self, service, anthropic_client):
        anthropic_client.messages.create.side_effect = anthropic.AuthenticationError(
            message="Invalid key", response=MagicMock(), body=None
        )
        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        with pytest.raises(AIAuthenticationError):
            service.explain(req)

    def test_connection_error_raises_domain_exception(self, service, anthropic_client):
        anthropic_client.messages.create.side_effect = anthropic.APIConnectionError(
            request=MagicMock()
        )
        req = ExplainRequest(
            suggestion=MOCK_SUGGESTION,
            original_code=VALID_CODE,
            language="python",
            deep=False,
        )
        with pytest.raises(AIUnavailableError):
            service.explain(req)

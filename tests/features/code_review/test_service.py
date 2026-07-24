# import anthropic
import openai
import pytest
from unittest.mock import MagicMock  # , patch
from core.exceptions import AIAuthenticationError, AIRateLimitError, AIUnavailableError

from features.code_review.models import ReviewRequest, Language  # ← agregar Language
from features.code_review.service import _extract_json
from core.config import AIProvider

CODE = "def calcular_promedio(n):\n    return sum(n)/len(n)"


# ── _extract_json ──────────────────────────────────────────────────
def test_extract_json_plain():
    assert _extract_json('{"key": "value"}') == '{"key": "value"}'


def test_extract_json_strips_markdown_fences():
    assert _extract_json('```json\n{"key": "value"}\n```') == '{"key": "value"}'


def test_extract_json_strips_fences_without_language():
    assert _extract_json('```\n{"key": "value"}\n```') == '{"key": "value"}'


# ── Error handling ─────────────────────────────────────────────────
def test_ollama_connection_error_raises_unavailable(
    mock_ollama_service, mock_ollama_client
):
    mock_ollama_client.chat.completions.create.side_effect = openai.APIConnectionError(
        request=MagicMock()
    )
    with pytest.raises(AIUnavailableError):
        mock_ollama_service.review(
            ReviewRequest(code=CODE, language=Language.python, context=None, deep=False)
        )


def test_ollama_auth_error_raises_authentication(
    mock_ollama_service, mock_ollama_client
):
    mock_ollama_client.chat.completions.create.side_effect = openai.AuthenticationError(
        message="Invalid key", response=MagicMock(), body={}
    )
    with pytest.raises(AIAuthenticationError):
        mock_ollama_service.review(
            ReviewRequest(code=CODE, language=Language.python, context=None, deep=False)
        )


def test_ollama_rate_limit_raises_rate_limit(mock_ollama_service, mock_ollama_client):
    mock_ollama_client.chat.completions.create.side_effect = openai.RateLimitError(
        message="Too many requests", response=MagicMock(), body={}
    )
    with pytest.raises(AIRateLimitError):
        mock_ollama_service.review(
            ReviewRequest(code=CODE, language=Language.python, context=None, deep=False)
        )


# ── Provider ───────────────────────────────────────────────────────
def test_ollama_service_provider(mock_ollama_service):
    assert mock_ollama_service.provider == AIProvider.ollama
    assert mock_ollama_service.is_anthropic is False


def test_anthropic_service_provider(mock_anthropic_service):
    assert mock_anthropic_service.provider == AIProvider.anthropic
    assert mock_anthropic_service.is_anthropic is True


# ── Model selection ────────────────────────────────────────────────
def test_get_model_fast(mock_ollama_service):
    assert "14b" in mock_ollama_service._get_model(deep=False)


def test_get_model_deep(mock_ollama_service):
    assert "32b" in mock_ollama_service._get_model(deep=True)


# ── Review ─────────────────────────────────────────────────────────
def test_review_ollama_returns_response(mock_ollama_service):
    result = mock_ollama_service.review(
        ReviewRequest(code=CODE, language=Language.python, context=None, deep=False)
    )
    assert result.language_detected == "python"
    assert result.overall_score == 6


def test_review_anthropic_returns_response(mock_anthropic_service):
    result = mock_anthropic_service.review(
        ReviewRequest(code=CODE, language=Language.python, context=None, deep=False)
    )
    assert result.language_detected == "python"
    assert result.overall_score == 6


def test_review_fast_calls_14b(mock_ollama_service, mock_ollama_client):
    mock_ollama_service.review(
        ReviewRequest(code=CODE, language=Language.python, context=None, deep=False)
    )
    model = mock_ollama_client.chat.completions.create.call_args.kwargs["model"]
    assert "14b" in model


def test_review_deep_calls_32b(mock_ollama_service, mock_ollama_client):
    mock_ollama_service.review(
        ReviewRequest(code=CODE, language=Language.python, context=None, deep=True)
    )
    model = mock_ollama_client.chat.completions.create.call_args.kwargs["model"]
    assert "32b" in model

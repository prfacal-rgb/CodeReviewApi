from unittest.mock import MagicMock

VALID_CODE = "def calcular_promedio(numeros):\n    return sum(numeros)/len(numeros)"


def test_review_success(api_client):
    response = api_client.post(
        "/reviews", json={"code": VALID_CODE, "language": "python"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["language_detected"] == "python"
    assert isinstance(data["suggestions"], list)
    assert 1 <= data["overall_score"] <= 10
    assert "refactored_code" in data


def test_review_uses_fast_model_by_default(api_client, mock_ollama_client):
    api_client.post("/reviews", json={"code": VALID_CODE})
    model = mock_ollama_client.chat.completions.create.call_args.kwargs["model"]
    assert "14b" in model


def test_review_uses_deep_model_when_requested(api_client, mock_ollama_client):
    api_client.post("/reviews", json={"code": VALID_CODE, "deep": True})
    model = mock_ollama_client.chat.completions.create.call_args.kwargs["model"]
    assert "32b" in model


def test_review_rejects_code_too_short(api_client):
    assert api_client.post("/reviews", json={"code": "x = 1"}).status_code == 422


def test_review_rejects_missing_code(api_client):
    assert api_client.post("/reviews", json={"language": "python"}).status_code == 422


def test_review_stream_success(api_client, mock_ollama_client):
    def make_chunk(content):
        chunk = MagicMock()
        chunk.choices[0].delta.content = content
        return chunk

    mock_ollama_client.chat.completions.create.return_value = iter(
        [
            make_chunk('{"language_detected": "python"'),
            make_chunk(', "summary": "ok"}'),
        ]
    )

    response = api_client.post("/reviews/stream", json={"code": VALID_CODE})
    assert response.status_code == 200
    assert "language_detected" in response.text

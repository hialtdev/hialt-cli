from unittest.mock import MagicMock, patch

import pytest
import requests

from hialt.providers.base import LLMResponse, ProviderError, StubProvider
from hialt.providers.ollama import OllamaProvider


def test_stub_provider_returns_llm_response():
    result = StubProvider().generate("hi")
    assert isinstance(result, LLMResponse)
    assert result.content == ""
    assert result.model == "stub"
    assert result.finish_reason == "stop"


def test_ollama_generate_parses_response_field():
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "response": "hello from llama",
        "done_reason": "stop",
        "prompt_eval_count": 3,
        "eval_count": 5,
        "model": "llama3.3",
    }

    with patch("hialt.providers.ollama.requests.post", return_value=mock_response) as post:
        provider = OllamaProvider(model="llama3.3", host="http://localhost:11434")
        result = provider.generate("hi", system="be brief")

    assert isinstance(result, LLMResponse)
    assert result.content == "hello from llama"
    assert result.usage.input_tokens == 3
    assert result.usage.output_tokens == 5
    assert result.model == "llama3.3"
    post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.3",
            "prompt": "hi",
            "stream": False,
            "system": "be brief",
        },
        timeout=60,
    )


def test_ollama_generate_omits_system_when_none():
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"response": "ok"}

    with patch("hialt.providers.ollama.requests.post", return_value=mock_response) as post:
        provider = OllamaProvider()
        provider.generate("prompt only")

    _, kwargs = post.call_args
    assert "system" not in kwargs["json"]


def test_ollama_generate_raises_provider_error_on_connection_failure():
    with patch(
        "hialt.providers.ollama.requests.post",
        side_effect=requests.ConnectionError("refused"),
    ):
        provider = OllamaProvider()
        with pytest.raises(ProviderError, match="Ollama request") as exc_info:
            provider.generate("hi")

    assert isinstance(exc_info.value.__cause__, requests.ConnectionError)


def test_ollama_generate_raises_provider_error_on_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("500")

    with patch("hialt.providers.ollama.requests.post", return_value=mock_response):
        provider = OllamaProvider()
        with pytest.raises(ProviderError, match="Ollama request") as exc_info:
            provider.generate("hi")

    assert isinstance(exc_info.value.__cause__, requests.HTTPError)

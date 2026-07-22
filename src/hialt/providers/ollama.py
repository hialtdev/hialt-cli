import logging

import requests

from hialt.providers.base import LLMResponse, ProviderError, TokenUsage

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_SECONDS = 60


class OllamaProvider:
    """Ollama /api/generate provider for local models."""

    def __init__(
        self,
        model: str = "llama3.3",
        host: str = "http://localhost:11434",
    ) -> None:
        self._model = model
        self._host = host.rstrip("/")

    def generate(self, prompt: str, system: str | None = None) -> LLMResponse:
        logger.debug("Sending Ollama generation request to %s", self._host)
        payload: dict = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }
        if system is not None:
            payload["system"] = system

        url = f"{self._host}/api/generate"
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=_DEFAULT_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("Ollama request failed: %s", exc)
            raise ProviderError(
                f"Ollama request to {url} failed: {exc}"
            ) from exc

        if "response" not in data:
            raise ProviderError(
                f"Ollama response from {url} missing 'response' field"
            )

        return LLMResponse(
            content=str(data["response"]),
            finish_reason=str(data.get("done_reason") or "stop"),
            usage=TokenUsage(
                input_tokens=int(data.get("prompt_eval_count") or 0),
                output_tokens=int(data.get("eval_count") or 0),
            ),
            model=str(data.get("model") or self._model),
            raw_response=data,
        )

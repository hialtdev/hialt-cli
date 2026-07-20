import requests

from hialt.providers.base import ProviderError

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

    def generate(self, prompt: str, system: str | None = None) -> str:
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
            raise ProviderError(
                f"Ollama request to {url} failed: {exc}"
            ) from exc

        if "response" not in data:
            raise ProviderError(
                f"Ollama response from {url} missing 'response' field"
            )
        return str(data["response"])

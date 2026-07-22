import os
import logging

from anthropic import Anthropic

from hialt.providers.base import LLMResponse, TokenUsage

logger = logging.getLogger(__name__)


class AnthropicProvider:
    """Anthropic Messages API provider. Reads ANTHROPIC_API_KEY from the environment."""

    def __init__(self, model: str = "claude-sonnet-4-6") -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self._model = model
        self._client = Anthropic(api_key=api_key)

    def generate(self, prompt: str, system: str | None = None) -> LLMResponse:
        logger.debug("Sending Anthropic generation request")
        kwargs: dict = {
            "model": self._model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system is not None:
            kwargs["system"] = system
        response = self._client.messages.create(**kwargs)
        content = "".join(
            block.text for block in response.content if hasattr(block, "text")
        )
        usage = TokenUsage()
        if response.usage is not None:
            usage = TokenUsage(
                input_tokens=int(getattr(response.usage, "input_tokens", 0) or 0),
                output_tokens=int(getattr(response.usage, "output_tokens", 0) or 0),
            )
        return LLMResponse(
            content=content,
            finish_reason=str(response.stop_reason or "stop"),
            usage=usage,
            model=str(response.model or self._model),
            raw_response=response,
        )

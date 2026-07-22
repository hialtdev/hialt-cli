import logging
from typing import Any, Protocol

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0


class LLMResponse(BaseModel):
    content: str
    finish_reason: str
    usage: TokenUsage = Field(default_factory=TokenUsage)
    model: str
    raw_response: Any = None


class ProviderError(Exception):
    """Raised when a provider request fails."""


class Provider(Protocol):
    def generate(self, prompt: str, system: str | None = None) -> LLMResponse:
        """Generate a completion for the given prompt."""
        ...


class StubProvider:
    """No-op provider for stub agent runs that do not call an LLM."""

    def generate(self, prompt: str, system: str | None = None) -> LLMResponse:
        return LLMResponse(
            content="",
            finish_reason="stop",
            usage=TokenUsage(),
            model="stub",
            raw_response=None,
        )

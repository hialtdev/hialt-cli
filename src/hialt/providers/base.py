import logging
from typing import Any, Protocol

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TokenUsage(BaseModel):
    """Normalize provider-reported token counts across vendor responses."""
    input_tokens: int = 0
    output_tokens: int = 0


class LLMResponse(BaseModel):
    """Carry normalized generation output without coupling agents to a vendor SDK."""
    content: str
    finish_reason: str
    usage: TokenUsage = Field(default_factory=TokenUsage)
    model: str
    raw_response: Any = None


class ProviderError(Exception):
    """Raised when a provider request fails."""


class Provider(Protocol):
    """Define the provider-independent reasoning capability consumed by agents."""
    def generate(self, prompt: str, system: str | None = None) -> LLMResponse:
        """Generate one normalized completion for a prompt and optional system context."""
        ...


class StubProvider:
    """No-op provider for stub agent runs that do not call an LLM."""

    def generate(self, prompt: str, system: str | None = None) -> LLMResponse:
        """Return an empty response so stub agents run without an external model."""
        return LLMResponse(
            content="",
            finish_reason="stop",
            usage=TokenUsage(),
            model="stub",
            raw_response=None,
        )

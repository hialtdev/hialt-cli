"""Build Provider instances from RoleConfig without coupling the graph to vendors."""

from __future__ import annotations

import logging

from hialt.providers.anthropic import AnthropicProvider
from hialt.providers.base import Provider, StubProvider
from hialt.providers.ollama import OllamaProvider
from hialt.settings import RoleConfig

logger = logging.getLogger(__name__)


def build_provider(config: RoleConfig) -> Provider:
    """Construct a Provider for a role. Graph code should only depend on Provider."""
    name = config.provider.lower()
    logger.debug("Building provider=%s model=%s", name, config.model)

    if name in {"stub", "local"}:
        return StubProvider()
    if name == "ollama":
        kwargs: dict = {}
        if config.model:
            kwargs["model"] = config.model
        return OllamaProvider(**kwargs)
    if name == "anthropic":
        kwargs = {}
        if config.model:
            kwargs["model"] = config.model
        return AnthropicProvider(**kwargs)

    # Reserved for future coding/reasoning engines (codex, openai, gemini, openrouter).
    raise ValueError(
        f"Unsupported provider {config.provider!r}. "
        "Supported today: stub, local, ollama, anthropic."
    )

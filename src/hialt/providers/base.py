from typing import Protocol


class Provider(Protocol):
    def generate(self, prompt: str, system: str | None = None) -> str:
        """Generate a completion for the given prompt."""
        ...


class StubProvider:
    """No-op provider for stub agent runs that do not call an LLM."""

    def generate(self, prompt: str, system: str | None = None) -> str:
        return ""

from typing import Protocol


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str:
        """Return a completion for the given prompt."""
        ...

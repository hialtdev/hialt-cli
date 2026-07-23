import logging

from hialt.providers.base import Provider
from hialt.state import CriticIssue, ExecutionPlan

logger = logging.getLogger(__name__)


class CoderAgent:
    """Own the coding capability boundary; coding behavior is currently a stub."""

    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def code(self, plan: ExecutionPlan, feedback: list[CriticIssue]) -> str:
        """Return placeholder code; this stub does not use feedback or its provider."""
        logger.debug("Rendering coder response")
        _ = feedback
        return f"[placeholder code for: {plan.objective}]"

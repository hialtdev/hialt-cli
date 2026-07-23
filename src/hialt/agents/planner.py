import logging

from hialt.providers.base import Provider
from hialt.state import ExecutionPlan

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Own the planning capability boundary; planning behavior is currently a stub."""

    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def plan(self, task: str) -> ExecutionPlan:
        """Return a placeholder plan; this stub does not call its provider."""
        logger.debug("Rendering planner response")
        return ExecutionPlan(
            objective=f"[placeholder plan for: {task}]",
            assumptions=[],
            implementation_steps=[],
            files_affected=[],
            acceptance_criteria=[],
        )

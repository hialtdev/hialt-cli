import logging

from hialt.providers.base import Provider
from hialt.state import ExecutionPlan

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def plan(self, task: str) -> ExecutionPlan:
        # Stub: real prompting via self._provider.generate(...) comes later.
        logger.debug("Rendering planner response")
        return ExecutionPlan(
            objective=f"[placeholder plan for: {task}]",
            assumptions=[],
            implementation_steps=[],
            files_affected=[],
            acceptance_criteria=[],
        )

from hialt.providers.base import Provider
from hialt.state import ExecutionPlan


class PlannerAgent:
    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def plan(self, task: str) -> ExecutionPlan:
        # Stub: real prompting via self._provider.generate(...) comes later.
        return ExecutionPlan(
            objective=f"[placeholder plan for: {task}]",
            assumptions=[],
            implementation_steps=[],
            files_affected=[],
            acceptance_criteria=[],
        )

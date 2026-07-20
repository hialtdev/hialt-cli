from hialt.providers.base import Provider
from hialt.state import CriticIssue, ExecutionPlan


class CoderAgent:
    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def code(self, plan: ExecutionPlan, feedback: list[CriticIssue]) -> str:
        # Stub: real prompting via self._provider.generate(...) comes later.
        _ = feedback
        return f"[placeholder code for: {plan.objective}]"

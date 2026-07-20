from hialt.providers.base import Provider
from hialt.state import CriticIssue, ExecutionPlan


class CriticAgent:
    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def review(self, plan: ExecutionPlan, code: str) -> list[CriticIssue]:
        # Stub: real prompting via self._provider.generate(...) comes later.
        _ = plan, code
        return []

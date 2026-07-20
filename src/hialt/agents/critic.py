import json_repair
from pydantic import ValidationError

from hialt.providers.base import Provider
from hialt.state import CriticIssue, ExecutionPlan

_PARSE_ERROR_RECOMMENDATION = (
    "Critic output for this item could not be parsed; review raw model output."
)
_TRUNCATE = 500


class CriticAgent:
    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    def review(self, plan: ExecutionPlan, code: str) -> list[CriticIssue]:
        # Stub: real prompting via self._provider.generate(...) comes later.
        # TODO: _build_prompt(plan, code) — prompt construction is written separately.
        _ = plan, code
        return []

    def _parse_response(self, raw: str) -> list[CriticIssue]:
        try:
            parsed = json_repair.loads(raw)
        except Exception:
            return [self._fallback_issue(raw)]

        if not isinstance(parsed, list):
            return [self._fallback_issue(raw)]

        issues: list[CriticIssue] = []
        for item in parsed:
            try:
                issues.append(CriticIssue.model_validate(item))
            except ValidationError:
                issues.append(self._fallback_issue(item))
        return issues

    @staticmethod
    def _fallback_issue(source: object) -> CriticIssue:
        return CriticIssue(
            description=repr(source)[:_TRUNCATE],
            severity="major",
            category="parse_error",
            confidence=0.0,
            recommendation=_PARSE_ERROR_RECOMMENDATION,
            location=None,
        )

from hialt.state import ToolResult, VerificationResult
from hialt.tools.runner import ToolRunner


class VerifierAgent:
    """Runs objective tool checks (pytest/ruff/mypy). No LLM judgment."""

    def __init__(self, tool_runner: ToolRunner | None = None) -> None:
        self._runner = tool_runner or ToolRunner()

    def verify(self, path: str | None = None) -> VerificationResult:
        results = [
            self._runner.run_pytest(path),
            self._runner.run_ruff(path),
            self._runner.run_mypy(path),
        ]
        passed = all(result.success for result in results)
        return VerificationResult(
            passed=passed,
            results=results,
            summary=self._summary(results),
        )

    @staticmethod
    def _summary(results: list[ToolResult]) -> str:
        parts: list[str] = []
        for result in results:
            if result.success:
                parts.append(f"{result.tool}: ok")
            else:
                parts.append(f"{result.tool}: failed (exit {result.exit_code})")
        return ", ".join(parts)

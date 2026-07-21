from unittest.mock import MagicMock

from hialt.agents.verifier import VerifierAgent
from hialt.state import ToolResult, VerificationResult


def _tool(name: str, success: bool, exit_code: int = 0) -> ToolResult:
    return ToolResult(
        tool=name,
        success=success,
        exit_code=exit_code if not success else 0,
        stdout="out",
        stderr="" if success else "err",
        duration_seconds=0.01,
    )


def test_verify_passed_when_all_tools_succeed():
    runner = MagicMock()
    runner.run_pytest.return_value = _tool("pytest", True)
    runner.run_ruff.return_value = _tool("ruff", True)
    runner.run_mypy.return_value = _tool("mypy", True)

    result = VerifierAgent(tool_runner=runner).verify("src/")

    assert isinstance(result, VerificationResult)
    assert result.passed is True
    assert len(result.results) == 3
    assert "pytest: ok" in result.summary
    assert "ruff: ok" in result.summary
    assert "mypy: ok" in result.summary
    runner.run_pytest.assert_called_once_with("src/")
    runner.run_ruff.assert_called_once_with("src/")
    runner.run_mypy.assert_called_once_with("src/")


def test_verify_failed_when_any_tool_fails():
    runner = MagicMock()
    runner.run_pytest.return_value = _tool("pytest", True)
    runner.run_ruff.return_value = _tool("ruff", False, exit_code=1)
    runner.run_mypy.return_value = _tool("mypy", True)

    result = VerifierAgent(tool_runner=runner).verify()

    assert result.passed is False
    assert "ruff: failed (exit 1)" in result.summary


def test_verify_summary_is_mechanical_not_empty():
    runner = MagicMock()
    runner.run_pytest.return_value = _tool("pytest", False, exit_code=2)
    runner.run_ruff.return_value = _tool("ruff", False, exit_code=1)
    runner.run_mypy.return_value = _tool("mypy", False, exit_code=1)

    result = VerifierAgent(tool_runner=runner).verify()

    assert result.passed is False
    assert result.summary == (
        "pytest: failed (exit 2), ruff: failed (exit 1), mypy: failed (exit 1)"
    )

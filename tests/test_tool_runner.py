from unittest.mock import MagicMock, patch

from hialt.state import ToolResult
from hialt.tools.runner import ToolRunner


def _completed(returncode: int = 0, stdout: str = "ok", stderr: str = "") -> MagicMock:
    completed = MagicMock()
    completed.returncode = returncode
    completed.stdout = stdout
    completed.stderr = stderr
    return completed


def test_run_pytest_success():
    runner = ToolRunner()
    with patch("hialt.tools.runner.subprocess.run", return_value=_completed(0, "passed")) as run:
        result = runner.run_pytest("tests/")

    assert isinstance(result, ToolResult)
    assert result.tool == "pytest"
    assert result.success is True
    assert result.exit_code == 0
    assert result.stdout == "passed"
    run.assert_called_once()
    assert run.call_args.args[0] == ["pytest", "tests/"]


def test_run_pytest_without_path():
    runner = ToolRunner()
    with patch("hialt.tools.runner.subprocess.run", return_value=_completed()) as run:
        runner.run_pytest()

    assert run.call_args.args[0] == ["pytest"]


def test_run_ruff_failure_returns_tool_result():
    runner = ToolRunner()
    with patch(
        "hialt.tools.runner.subprocess.run",
        return_value=_completed(1, "", "E501"),
    ):
        result = runner.run_ruff("src/")

    assert result.tool == "ruff"
    assert result.success is False
    assert result.exit_code == 1
    assert result.stderr == "E501"


def test_run_mypy_command_shape():
    runner = ToolRunner()
    with patch("hialt.tools.runner.subprocess.run", return_value=_completed()) as run:
        runner.run_mypy()

    assert run.call_args.args[0] == ["mypy", "."]


def test_timeout_returns_unsuccessful_tool_result():
    import subprocess

    runner = ToolRunner(timeout_seconds=1.0)
    with patch(
        "hialt.tools.runner.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd=["pytest"], timeout=1.0),
    ):
        result = runner.run_pytest()

    assert result.success is False
    assert result.exit_code == -1
    assert "timed out" in result.stderr


def test_oserror_returns_unsuccessful_tool_result():
    runner = ToolRunner()
    with patch(
        "hialt.tools.runner.subprocess.run",
        side_effect=FileNotFoundError("pytest not found"),
    ):
        result = runner.run_pytest()

    assert result.success is False
    assert result.exit_code == -1
    assert "pytest not found" in result.stderr

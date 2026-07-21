import subprocess
import time

from hialt.state import ToolResult

_DEFAULT_TIMEOUT_SECONDS = 60.0


class ToolRunner:
    """Sole component allowed to shell out or touch the subprocess/filesystem boundary."""

    def __init__(self, timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def run_pytest(self, path: str | None = None) -> ToolResult:
        cmd = ["pytest"]
        if path:
            cmd.append(path)
        return self._run("pytest", cmd)

    def run_ruff(self, path: str | None = None) -> ToolResult:
        cmd = ["ruff", "check", path or "."]
        return self._run("ruff", cmd)

    def run_mypy(self, path: str | None = None) -> ToolResult:
        cmd = ["mypy", path or "."]
        return self._run("mypy", cmd)

    def _run(self, tool: str, cmd: list[str]) -> ToolResult:
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
            duration = time.perf_counter() - started
            return ToolResult(
                tool=tool,
                success=completed.returncode == 0,
                exit_code=completed.returncode,
                stdout=completed.stdout or "",
                stderr=completed.stderr or "",
                duration_seconds=duration,
            )
        except subprocess.TimeoutExpired as exc:
            duration = time.perf_counter() - started
            stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return ToolResult(
                tool=tool,
                success=False,
                exit_code=-1,
                stdout=stdout,
                stderr=stderr or f"timed out after {self._timeout_seconds}s",
                duration_seconds=duration,
            )
        except OSError as exc:
            duration = time.perf_counter() - started
            return ToolResult(
                tool=tool,
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(exc),
                duration_seconds=duration,
            )

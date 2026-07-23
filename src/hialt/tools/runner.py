import logging
import subprocess
import time
from collections.abc import Sequence

from hialt.state import ToolResult

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_SECONDS = 60.0


class ToolRunner:
    """Sole component allowed to shell out or touch the subprocess/filesystem boundary."""

    def __init__(self, timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def run_pytest(self, path: str | None = None) -> ToolResult:
        """Run pytest through the deterministic subprocess boundary."""
        cmd = ["pytest"]
        if path:
            cmd.append(path)
        return self.run("pytest", cmd)

    def run_ruff(self, path: str | None = None) -> ToolResult:
        """Run Ruff through the deterministic subprocess boundary."""
        cmd = ["ruff", "check", path or "."]
        return self.run("ruff", cmd)

    def run_mypy(self, path: str | None = None) -> ToolResult:
        """Run MyPy through the deterministic subprocess boundary."""
        cmd = ["mypy", path or "."]
        return self.run("mypy", cmd)

    def run(self, tool: str, command: Sequence[str]) -> ToolResult:
        """Execute a deterministic command for a focused tool adapter.

        Future filesystem, git, and quality-check modules can own their command
        construction while this class remains the sole subprocess boundary.
        """
        logger.debug("Running deterministic tool: %s", tool)
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                list(command),
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
            duration = time.perf_counter() - started
            logger.info(
                "Tool %s completed: success=%s duration=%.2fs",
                tool,
                completed.returncode == 0,
                duration,
            )
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
            logger.warning("Tool %s timed out after %.2fs", tool, duration)
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
            logger.error("Tool %s could not start: %s", tool, exc)
            return ToolResult(
                tool=tool,
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(exc),
                duration_seconds=duration,
            )

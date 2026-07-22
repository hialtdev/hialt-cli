"""Runtime configuration owned by the application, not individual modules."""

from __future__ import annotations

from functools import lru_cache
import logging
import os

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RoleConfig(BaseModel):
    """Independent provider + model selection for one graph role."""

    provider: str = "stub"
    model: str | None = None


class Settings(BaseModel):
    log_level: str = "INFO"
    max_iterations: int = 3
    tool_timeout_seconds: float = 60.0
    default_provider: str = "stub"
    retry_attempts: int = 1
    approval_blocking_severity: str = "blocking"

    planner: RoleConfig = Field(default_factory=RoleConfig)
    coder: RoleConfig = Field(default_factory=RoleConfig)
    critic: RoleConfig = Field(default_factory=RoleConfig)
    # Verifier is deterministic/local today; provider slot reserved for future engines.
    verifier: RoleConfig = Field(
        default_factory=lambda: RoleConfig(provider="local", model=None)
    )

    @classmethod
    def from_environment(cls) -> "Settings":
        """Build settings from the small set of process-level overrides we support."""
        return cls(
            log_level=os.getenv("HIALT_LOG_LEVEL", "INFO"),
            max_iterations=int(os.getenv("HIALT_MAX_ITERATIONS", "3")),
            tool_timeout_seconds=float(
                os.getenv("HIALT_TOOL_TIMEOUT_SECONDS", "60")
            ),
            retry_attempts=int(os.getenv("HIALT_RETRY_ATTEMPTS", "1")),
            approval_blocking_severity=os.getenv(
                "HIALT_APPROVAL_BLOCKING_SEVERITY", "blocking"
            ),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return process-wide defaults; pass Settings explicitly across boundaries."""
    return Settings.from_environment()

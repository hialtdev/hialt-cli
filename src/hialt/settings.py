"""Runtime settings. Providers and tools should read configuration from here."""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel, Field


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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return process-wide settings. Cached; no DI container."""
    return Settings()

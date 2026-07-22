import logging

logger = logging.getLogger(__name__)


def failure_envelope(
    status: str,
    message: str,
    detail: dict | None = None,
) -> dict:
    """Return a minimal, reusable failure payload for CLI/API callers."""
    return {
        "status": status,
        "message": message,
        "detail": detail or {},
    }


def critic_issue_parse_failure(raw: str) -> dict:
    """Failure envelope for critic responses that could not be parsed."""
    return failure_envelope(
        status="parse_error",
        message="critic response could not be parsed",
        detail={"raw": raw[:500]},
    )

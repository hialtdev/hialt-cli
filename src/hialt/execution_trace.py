"""Agent flight recorder: how the graph executed (not application logging)."""

from datetime import datetime, timezone
from enum import Enum
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class TraceEvent(str, Enum):
    GRAPH_STARTED = "graph_started"
    PLANNING_STARTED = "planning_started"
    PLANNING_COMPLETED = "planning_completed"
    CODING_STARTED = "coding_started"
    CODING_COMPLETED = "coding_completed"
    TOOL_REQUESTED = "tool_requested"
    TOOL_COMPLETED = "tool_completed"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_COMPLETED = "verification_completed"
    CRITIQUE_STARTED = "critique_started"
    CRITIQUE_COMPLETED = "critique_completed"
    REVISION_REQUESTED = "revision_requested"
    ITERATION_INCREMENTED = "iteration_incremented"
    APPROVED = "approved"
    FAILED = "failed"


class TraceEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    node: str
    event_type: TraceEvent
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


def make_trace_entry(
    node: str,
    event_type: TraceEvent,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> TraceEntry:
    logger.debug("Trace entry recorded: node=%s event=%s", node, event_type.value)
    return TraceEntry(
        timestamp=datetime.now(timezone.utc),
        node=node,
        event_type=event_type,
        message=message,
        metadata=metadata or {},
    )

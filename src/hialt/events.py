from datetime import datetime, timezone
from typing import Any

from hialt.state import AgentEvent, EventType


def make_event(
    node: str,
    event_type: EventType,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> AgentEvent:
    return AgentEvent(
        timestamp=datetime.now(timezone.utc),
        node=node,
        event_type=event_type,
        message=message,
        metadata=metadata or {},
    )

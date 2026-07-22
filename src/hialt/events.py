"""Deprecated compatibility imports for the former event subsystem.

New code must use :mod:`hialt.execution_trace` directly.
"""

import logging

from hialt.execution_trace import TraceEntry, TraceEvent, make_trace_entry

logger = logging.getLogger(__name__)

AgentEvent = TraceEntry
EventType = TraceEvent
make_event = make_trace_entry

__all__ = ["AgentEvent", "EventType", "make_event"]

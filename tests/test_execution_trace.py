import operator
from datetime import datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from hialt.agents.graph import build_graph, coder_node, planner_node
from hialt.events import make_event
from hialt.state import AgentEvent, AgentState, EventType, ToolResult, VerificationResult


def _passing_verification() -> VerificationResult:
    return VerificationResult(
        passed=True,
        results=[
            ToolResult(
                tool="pytest",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                duration_seconds=0.01,
            ),
            ToolResult(
                tool="ruff",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                duration_seconds=0.01,
            ),
            ToolResult(
                tool="mypy",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                duration_seconds=0.01,
            ),
        ],
        summary="pytest: ok, ruff: ok, mypy: ok",
    )


def _base_state(**overrides) -> AgentState:
    state: AgentState = {
        "task": "demo",
        "plan": None,
        "current_code": "",
        "critic_feedback": [],
        "verification_result": None,
        "iteration": 0,
        "status": "planning",
        "trace": [],
    }
    state.update(overrides)
    return state


def test_agent_event_is_frozen():
    event = make_event("planner", EventType.PLANNING_STARTED, "Planning started")
    with pytest.raises(ValidationError):
        event.message = "mutated"  # type: ignore[misc]


def test_trace_reducer_concatenates_partial_updates():
    first = [
        make_event("planner", EventType.PLANNING_STARTED, "Planning started"),
    ]
    second = [
        make_event("coder", EventType.CODING_STARTED, "Coding started"),
    ]
    merged = operator.add(first, second)
    assert len(merged) == 2
    assert merged[0].event_type == EventType.PLANNING_STARTED
    assert merged[1].event_type == EventType.CODING_STARTED


def test_nodes_append_started_and_completed_events():
    state = _base_state()
    after_plan = planner_node(state)
    assert any(e.event_type == EventType.PLANNING_STARTED for e in after_plan["trace"])
    assert any(e.event_type == EventType.PLANNING_COMPLETED for e in after_plan["trace"])

    mid: AgentState = {**state, **after_plan, "trace": []}
    after_code = coder_node(mid)
    assert any(e.event_type == EventType.CODING_STARTED for e in after_code["trace"])
    assert any(e.event_type == EventType.CODING_COMPLETED for e in after_code["trace"])


def test_graph_run_appends_trace_across_nodes():
    with patch(
        "hialt.agents.graph.VerifierAgent.verify",
        return_value=_passing_verification(),
    ):
        graph = build_graph()
        final = graph.invoke(
            _base_state(),
            config={"configurable": {"thread_id": "trace-test"}},
        )

    trace = final["trace"]
    assert len(trace) >= 4
    types = [event.event_type for event in trace]
    assert EventType.GRAPH_STARTED in types
    assert EventType.PLANNING_COMPLETED in types
    assert EventType.CODING_COMPLETED in types
    assert EventType.VERIFICATION_COMPLETED in types
    assert EventType.CRITIQUE_COMPLETED in types
    assert EventType.APPROVED in types
    # Events are appended, not overwritten to a single node snapshot
    assert types.count(EventType.CODING_COMPLETED) >= 1
    assert all(isinstance(event, AgentEvent) for event in trace)
    assert all(isinstance(event.timestamp, datetime) for event in trace)
    assert all(event.timestamp.tzinfo is not None for event in trace)

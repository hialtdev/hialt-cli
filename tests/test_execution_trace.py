import operator
from datetime import datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from hialt.agents.graph import build_graph, coder_node, planner_node
from hialt.execution_trace import TraceEntry, TraceEvent, make_trace_entry
from hialt.state import AgentState, ToolResult, VerificationResult


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
        "execution_trace": [],
    }
    state.update(overrides) # type: ignore[arg-type]
    return state


def test_agent_event_is_frozen():
    event = make_trace_entry("planner", TraceEvent.PLANNING_STARTED, "Planning started")
    with pytest.raises(ValidationError):
        event.message = "mutated"  # type: ignore[misc]


def test_trace_reducer_concatenates_partial_updates():
    first = [
        make_trace_entry("planner", TraceEvent.PLANNING_STARTED, "Planning started"),
    ]
    second = [
        make_trace_entry("coder", TraceEvent.CODING_STARTED, "Coding started"),
    ]
    merged = operator.add(first, second)
    assert len(merged) == 2
    assert merged[0].event_type == TraceEvent.PLANNING_STARTED
    assert merged[1].event_type == TraceEvent.CODING_STARTED


def test_nodes_append_started_and_completed_events():
    state = _base_state()
    after_plan = planner_node(state)
    assert any(e.event_type == TraceEvent.PLANNING_STARTED for e in after_plan["execution_trace"])
    assert any(e.event_type == TraceEvent.PLANNING_COMPLETED for e in after_plan["execution_trace"])

    mid: AgentState = {**state, **after_plan, "execution_trace": []}  # type: ignore[assignment]
    after_code = coder_node(mid)
    assert any(e.event_type == TraceEvent.CODING_STARTED for e in after_code["execution_trace"])
    assert any(e.event_type == TraceEvent.CODING_COMPLETED for e in after_code["execution_trace"])


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

    trace = final["execution_trace"]
    assert len(trace) >= 4
    types = [event.event_type for event in trace]
    assert TraceEvent.GRAPH_STARTED in types
    assert TraceEvent.PLANNING_COMPLETED in types
    assert TraceEvent.CODING_COMPLETED in types
    assert TraceEvent.VERIFICATION_COMPLETED in types
    assert TraceEvent.CRITIQUE_COMPLETED in types
    assert TraceEvent.APPROVED in types
    # Events are appended, not overwritten to a single node snapshot
    assert types.count(TraceEvent.CODING_COMPLETED) >= 1
    assert all(isinstance(event, TraceEntry) for event in trace)
    assert all(isinstance(event.timestamp, datetime) for event in trace)
    assert all(event.timestamp.tzinfo is not None for event in trace)
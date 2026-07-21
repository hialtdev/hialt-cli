from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from hialt.agents.coder import CoderAgent
from hialt.agents.critic import CriticAgent
from hialt.agents.planner import PlannerAgent
from hialt.agents.verifier import VerifierAgent
from hialt.events import make_event
from hialt.providers.base import Provider, StubProvider
from hialt.state import AgentState, EventType, ExecutionPlan

Route = Literal["revise", "approved", "failed"]
VerifierRoute = Literal["revise", "critic", "failed"]

_DEFAULT_PROVIDER: Provider = StubProvider()


def _ensure_plan(state: AgentState) -> ExecutionPlan:
    plan = state["plan"]
    if plan is not None:
        return plan
    return ExecutionPlan(
        objective=state["task"],
        assumptions=[],
        implementation_steps=[],
        files_affected=[],
        acceptance_criteria=[],
    )


def planner_node(state: AgentState) -> dict:
    events = [
        make_event("planner", EventType.GRAPH_STARTED, "Graph started"),
        make_event("planner", EventType.PLANNING_STARTED, "Planning started"),
    ]
    agent = PlannerAgent(_DEFAULT_PROVIDER)
    plan = agent.plan(state["task"])
    events.append(
        make_event(
            "planner",
            EventType.PLANNING_COMPLETED,
            f"Planning completed: {plan.objective}",
            {"objective": plan.objective},
        )
    )
    return {
        "plan": plan,
        "status": "planning",
        "trace": events,
    }


def coder_node(state: AgentState) -> dict:
    events = [
        make_event("coder", EventType.CODING_STARTED, "Coding started"),
    ]
    plan = _ensure_plan(state)
    agent = CoderAgent(_DEFAULT_PROVIDER)
    code = agent.code(plan, state["critic_feedback"])
    events.append(
        make_event(
            "coder",
            EventType.CODING_COMPLETED,
            "Coding completed",
            {"code_chars": len(code)},
        )
    )
    return {
        "current_code": code,
        "status": "coding",
        "trace": events,
    }


def verifier_node(state: AgentState) -> dict:
    events = [
        make_event(
            "verifier",
            EventType.VERIFICATION_STARTED,
            "Verification started",
        ),
    ]
    agent = VerifierAgent()
    for tool_name in ("pytest", "ruff", "mypy"):
        events.append(
            make_event(
                "verifier",
                EventType.TOOL_REQUESTED,
                f"Tool requested: {tool_name}",
                {"tool": tool_name},
            )
        )

    result = agent.verify()

    for tool_result in result.results:
        events.append(
            make_event(
                "verifier",
                EventType.TOOL_COMPLETED,
                f"Tool completed: {tool_result.tool} "
                f"{'ok' if tool_result.success else 'failed'}",
                {
                    "tool": tool_result.tool,
                    "success": tool_result.success,
                    "exit_code": tool_result.exit_code,
                },
            )
        )

    events.append(
        make_event(
            "verifier",
            EventType.VERIFICATION_COMPLETED,
            f"Verifier completed: {result.summary}",
            {"passed": result.passed},
        )
    )
    return {
        "verification_result": result,
        "status": "verifying",
        "trace": events,
    }


def critic_node(state: AgentState) -> dict:
    events = [
        make_event("critic", EventType.CRITIQUE_STARTED, "Critique started"),
    ]
    plan = _ensure_plan(state)
    agent = CriticAgent(_DEFAULT_PROVIDER)
    issues = agent.review(plan, state["current_code"])
    events.append(
        make_event(
            "critic",
            EventType.CRITIQUE_COMPLETED,
            f"Critique completed: {len(issues)} issue(s)",
            {"issue_count": len(issues)},
        )
    )
    return {
        "critic_feedback": issues,
        "status": "reviewing",
        "trace": events,
    }


def increment_iteration(state: AgentState) -> dict:
    next_iteration = state["iteration"] + 1
    return {
        "iteration": next_iteration,
        "trace": [
            make_event(
                "increment_iteration",
                EventType.REVISION_REQUESTED,
                "Revision requested",
                {"iteration": next_iteration},
            ),
            make_event(
                "increment_iteration",
                EventType.ITERATION_INCREMENTED,
                f"Iteration incremented to {next_iteration}",
                {"iteration": next_iteration},
            ),
        ],
    }


def finalize_approved(state: AgentState) -> dict:
    return {
        "status": "approved",
        "trace": [
            make_event("finalize_approved", EventType.APPROVED, "Run approved"),
        ],
    }


def finalize_failed(state: AgentState) -> dict:
    return {
        "status": "failed",
        "trace": [
            make_event("finalize_failed", EventType.FAILED, "Run failed"),
        ],
    }


def route_after_verifier(state: AgentState) -> VerifierRoute:
    result = state.get("verification_result")
    if result is not None and result.passed:
        return "critic"
    if state["iteration"] < 3:
        return "revise"
    return "failed"


def route_after_critic(state: AgentState) -> Route:
    has_blocking = any(
        issue.severity == "blocking" for issue in state["critic_feedback"]
    )
    if has_blocking and state["iteration"] < 3:
        return "revise"
    if has_blocking:
        return "failed"
    return "approved"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("critic", critic_node)
    graph.add_node("increment_iteration", increment_iteration)
    graph.add_node("finalize_approved", finalize_approved)
    graph.add_node("finalize_failed", finalize_failed)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "verifier")
    graph.add_conditional_edges(
        "verifier",
        route_after_verifier,
        {
            "revise": "increment_iteration",
            "critic": "critic",
            "failed": "finalize_failed",
        },
    )
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "revise": "increment_iteration",
            "approved": "finalize_approved",
            "failed": "finalize_failed",
        },
    )
    graph.add_edge("increment_iteration", "coder")
    graph.add_edge("finalize_approved", END)
    graph.add_edge("finalize_failed", END)

    return graph.compile(checkpointer=MemorySaver())

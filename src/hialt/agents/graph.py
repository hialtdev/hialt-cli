"""LangGraph workflow composition for the HIALT orchestration agent."""

from dataclasses import dataclass
from functools import partial
import logging
from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from hialt.agents.coder import CoderAgent
from hialt.agents.critic import CriticAgent
from hialt.agents.planner import PlannerAgent
from hialt.agents.verifier import VerifierAgent
from hialt.execution_trace import TraceEntry, TraceEvent, make_trace_entry
from hialt.providers.base import Provider
from hialt.providers.factory import build_provider
from hialt.settings import Settings, get_settings
from hialt.state import AgentState, ExecutionPlan
from hialt.tools.runner import ToolRunner

logger = logging.getLogger(__name__)

Route = Literal["revise", "approved", "failed"]
VerifierRoute = Literal["revise", "critic", "failed"]


@dataclass(frozen=True)
class GraphDependencies:
    """Concrete graph dependencies assembled at the application boundary."""

    planner_provider: Provider
    coder_provider: Provider
    critic_provider: Provider
    tool_runner: ToolRunner
    max_iterations: int
    approval_blocking_severity: str

    @classmethod
    def from_settings(cls, settings: Settings) -> "GraphDependencies":
        return cls(
            planner_provider=build_provider(settings.planner),
            coder_provider=build_provider(settings.coder),
            critic_provider=build_provider(settings.critic),
            tool_runner=ToolRunner(timeout_seconds=settings.tool_timeout_seconds),
            max_iterations=settings.max_iterations,
            approval_blocking_severity=settings.approval_blocking_severity,
        )


def _trace_update(entries: list[TraceEntry]) -> dict[str, list[TraceEntry]]:
    """Write the canonical trace and a temporary compatibility mirror together."""
    return {"execution_trace": entries}


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


def planner_node(state: AgentState, provider: Provider | None = None) -> dict:
    logger.info("Planning task")
    entries = [
        make_trace_entry("planner", TraceEvent.GRAPH_STARTED, "Graph started"),
        make_trace_entry("planner", TraceEvent.PLANNING_STARTED, "Planning started"),
    ]
    agent = PlannerAgent(provider or build_provider(get_settings().planner))
    plan = agent.plan(state["task"])
    entries.append(
        make_trace_entry(
            "planner",
            TraceEvent.PLANNING_COMPLETED,
            f"Planning completed: {plan.objective}",
            {"objective": plan.objective},
        )
    )
    return {"plan": plan, "status": "planning", **_trace_update(entries)}


def coder_node(state: AgentState, provider: Provider | None = None) -> dict:
    logger.info("Coding plan")
    entries = [
        make_trace_entry("coder", TraceEvent.CODING_STARTED, "Coding started"),
    ]
    agent = CoderAgent(provider or build_provider(get_settings().coder))
    code = agent.code(_ensure_plan(state), state["critic_feedback"])
    entries.append(
        make_trace_entry(
            "coder",
            TraceEvent.CODING_COMPLETED,
            "Coding completed",
            {"code_chars": len(code)},
        )
    )
    return {"current_code": code, "status": "coding", **_trace_update(entries)}


def verifier_node(state: AgentState, tool_runner: ToolRunner | None = None) -> dict:
    logger.info("Verifying workspace")
    entries = [
        make_trace_entry(
            "verifier", TraceEvent.VERIFICATION_STARTED, "Verification started"
        )
    ]
    for tool_name in ("pytest", "ruff", "mypy"):
        entries.append(
            make_trace_entry(
                "verifier",
                TraceEvent.TOOL_REQUESTED,
                f"Tool requested: {tool_name}",
                {"tool": tool_name},
            )
        )

    result = VerifierAgent(tool_runner).verify()
    for tool_result in result.results:
        entries.append(
            make_trace_entry(
                "verifier",
                TraceEvent.TOOL_COMPLETED,
                f"Tool completed: {tool_result.tool} "
                f"{'ok' if tool_result.success else 'failed'}",
                {
                    "tool": tool_result.tool,
                    "success": tool_result.success,
                    "exit_code": tool_result.exit_code,
                },
            )
        )
    entries.append(
        make_trace_entry(
            "verifier",
            TraceEvent.VERIFICATION_COMPLETED,
            f"Verifier completed: {result.summary}",
            {"passed": result.passed},
        )
    )
    return {
        "verification_result": result,
        "status": "verifying",
        **_trace_update(entries),
    }


def critic_node(state: AgentState, provider: Provider | None = None) -> dict:
    logger.info("Reviewing result")
    entries = [
        make_trace_entry("critic", TraceEvent.CRITIQUE_STARTED, "Critique started"),
    ]
    issues = CriticAgent(provider or build_provider(get_settings().critic)).review(
        _ensure_plan(state), state["current_code"]
    )
    entries.append(
        make_trace_entry(
            "critic",
            TraceEvent.CRITIQUE_COMPLETED,
            f"Critique completed: {len(issues)} issue(s)",
            {"issue_count": len(issues)},
        )
    )
    return {"critic_feedback": issues, "status": "reviewing", **_trace_update(entries)}


def increment_iteration(state: AgentState) -> dict:
    next_iteration = state["iteration"] + 1
    logger.info("Starting revision iteration %s", next_iteration)
    return {
        "iteration": next_iteration,
        **_trace_update(
            [
                make_trace_entry(
                    "increment_iteration",
                    TraceEvent.REVISION_REQUESTED,
                    "Revision requested",
                    {"iteration": next_iteration},
                ),
                make_trace_entry(
                    "increment_iteration",
                    TraceEvent.ITERATION_INCREMENTED,
                    f"Iteration incremented to {next_iteration}",
                    {"iteration": next_iteration},
                ),
            ]
        ),
    }


def finalize_approved(state: AgentState) -> dict:
    logger.info("Run approved")
    return {
        "status": "approved",
        **_trace_update(
            [make_trace_entry("finalize_approved", TraceEvent.APPROVED, "Run approved")]
        ),
    }


def finalize_failed(state: AgentState) -> dict:
    logger.error("Run failed")
    return {
        "status": "failed",
        **_trace_update(
            [make_trace_entry("finalize_failed", TraceEvent.FAILED, "Run failed")]
        ),
    }


def route_after_verifier(
    state: AgentState, max_iterations: int | None = None
) -> VerifierRoute:
    result = state.get("verification_result")
    if result is not None and result.passed:
        return "critic"
    limit = max_iterations if max_iterations is not None else get_settings().max_iterations
    return "revise" if state["iteration"] < limit else "failed"


def route_after_critic(
    state: AgentState,
    max_iterations: int | None = None,
    blocking_severity: str | None = None,
) -> Route:
    severity = blocking_severity or get_settings().approval_blocking_severity
    has_blocking = any(
        issue.severity == severity for issue in state["critic_feedback"]
    )
    limit = max_iterations if max_iterations is not None else get_settings().max_iterations
    if has_blocking:
        return "revise" if state["iteration"] < limit else "failed"
    return "approved"


def build_graph(dependencies: GraphDependencies | None = None):
    """Build the workflow from explicit capability dependencies."""
    deps = dependencies or GraphDependencies.from_settings(get_settings())
    logger.debug("Building graph with max_iterations=%s", deps.max_iterations)
    graph = StateGraph(AgentState)
    graph.add_node("planner", partial(planner_node, provider=deps.planner_provider))
    graph.add_node("coder", partial(coder_node, provider=deps.coder_provider))
    graph.add_node("verifier", partial(verifier_node, tool_runner=deps.tool_runner))
    graph.add_node("critic", partial(critic_node, provider=deps.critic_provider))
    graph.add_node("increment_iteration", increment_iteration)
    graph.add_node("finalize_approved", finalize_approved)
    graph.add_node("finalize_failed", finalize_failed)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "verifier")
    graph.add_conditional_edges(
        "verifier",
        partial(route_after_verifier, max_iterations=deps.max_iterations),
        {"revise": "increment_iteration", "critic": "critic", "failed": "finalize_failed"},
    )
    graph.add_conditional_edges(
        "critic",
        partial(
            route_after_critic,
            max_iterations=deps.max_iterations,
            blocking_severity=deps.approval_blocking_severity,
        ),
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

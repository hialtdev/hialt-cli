from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from hialt.agents.coder import CoderAgent
from hialt.agents.critic import CriticAgent
from hialt.agents.planner import PlannerAgent
from hialt.providers.base import Provider, StubProvider
from hialt.state import AgentState, ExecutionPlan

Route = Literal["revise", "approved", "failed"]

_DEFAULT_PROVIDER: Provider = StubProvider()


def planner_node(state: AgentState) -> dict:
    agent = PlannerAgent(_DEFAULT_PROVIDER)
    return {
        "plan": agent.plan(state["task"]),
        "status": "planning",
    }


def coder_node(state: AgentState) -> dict:
    plan = state["plan"]
    if plan is None:
        plan = ExecutionPlan(
            objective=state["task"],
            assumptions=[],
            implementation_steps=[],
            files_affected=[],
            acceptance_criteria=[],
        )
    agent = CoderAgent(_DEFAULT_PROVIDER)
    return {
        "current_code": agent.code(plan, state["critic_feedback"]),
        "status": "coding",
    }


def critic_node(state: AgentState) -> dict:
    plan = state["plan"]
    if plan is None:
        plan = ExecutionPlan(
            objective=state["task"],
            assumptions=[],
            implementation_steps=[],
            files_affected=[],
            acceptance_criteria=[],
        )
    agent = CriticAgent(_DEFAULT_PROVIDER)
    return {
        "critic_feedback": agent.review(plan, state["current_code"]),
        "status": "reviewing",
    }


def increment_iteration(state: AgentState) -> dict:
    return {"iteration": state["iteration"] + 1}


def finalize_approved(state: AgentState) -> dict:
    return {"status": "approved"}


def finalize_failed(state: AgentState) -> dict:
    return {"status": "failed"}


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
    graph.add_node("critic", critic_node)
    graph.add_node("increment_iteration", increment_iteration)
    graph.add_node("finalize_approved", finalize_approved)
    graph.add_node("finalize_failed", finalize_failed)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "critic")
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

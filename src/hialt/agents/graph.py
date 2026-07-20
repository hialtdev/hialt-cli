from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from hialt.state import AgentState

Route = Literal["revise", "approved", "failed"]


def planner_node(state: AgentState) -> dict:
    # TODO: llm.complete(...) — produce a plan from state["task"]
    return {
        "plan": f"[placeholder plan for: {state['task']}]",
        "status": "planning",
    }


def coder_node(state: AgentState) -> dict:
    # TODO: llm.complete(...) — implement code from plan + critic_feedback
    return {
        "current_code": f"[placeholder code for: {state['task']}]",
        "status": "coding",
    }


def critic_node(state: AgentState) -> dict:
    # TODO: llm.complete(...) — adversarially review current_code against plan
    # Placeholder: return CriticIssue(...) list; empty means no findings.
    return {
        "critic_feedback": [],
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

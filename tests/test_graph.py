from hialt.agents.graph import route_after_critic
from hialt.state import AgentState, CriticIssue


def _base_state(**overrides) -> AgentState:
    state: AgentState = {
        "task": "demo",
        "plan": "plan",
        "current_code": "code",
        "critic_feedback": [],
        "iteration": 0,
        "status": "reviewing",
    }
    state.update(overrides)
    return state


def test_route_revise_when_blocking_and_iteration_under_limit():
    state = _base_state(
        iteration=1,
        critic_feedback=[
            CriticIssue(description="needs fix", severity="blocking"),
        ],
    )
    assert route_after_critic(state) == "revise"


def test_route_approved_when_no_blocking_issues():
    state = _base_state(
        iteration=0,
        critic_feedback=[
            CriticIssue(description="nit", severity="minor"),
            CriticIssue(description="smell", severity="major"),
        ],
    )
    assert route_after_critic(state) == "approved"


def test_route_failed_when_blocking_and_iteration_at_limit():
    state = _base_state(
        iteration=3,
        critic_feedback=[
            CriticIssue(description="still broken", severity="blocking"),
        ],
    )
    assert route_after_critic(state) == "failed"

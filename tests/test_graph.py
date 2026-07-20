from hialt.agents.graph import route_after_critic
from hialt.state import AgentState, CriticIssue


def _issue(
    description: str,
    severity: str,
    *,
    category: str = "general",
    confidence: float = 0.9,
    recommendation: str = "fix it",
) -> CriticIssue:
    return CriticIssue(
        description=description,
        severity=severity,  # type: ignore[arg-type]
        category=category,
        confidence=confidence,
        recommendation=recommendation,
    )


def _base_state(**overrides) -> AgentState:
    state: AgentState = {
        "task": "demo",
        "plan": None,
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
            _issue("needs fix", "blocking"),
        ],
    )
    assert route_after_critic(state) == "revise"


def test_route_approved_when_no_blocking_issues():
    state = _base_state(
        iteration=0,
        critic_feedback=[
            _issue("nit", "minor"),
            _issue("smell", "major"),
        ],
    )
    assert route_after_critic(state) == "approved"


def test_route_failed_when_blocking_and_iteration_at_limit():
    state = _base_state(
        iteration=3,
        critic_feedback=[
            _issue("still broken", "blocking"),
        ],
    )
    assert route_after_critic(state) == "failed"

from hialt.agents.graph import route_after_critic, route_after_verifier
from hialt.state import AgentState, CriticIssue, ToolResult, VerificationResult


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


def _tool(name: str, success: bool) -> ToolResult:
    return ToolResult(
        tool=name,
        success=success,
        exit_code=0 if success else 1,
        stdout="",
        stderr="" if success else "fail",
        duration_seconds=0.01,
    )


def _verification(passed: bool) -> VerificationResult:
    return VerificationResult(
        passed=passed,
        results=[
            _tool("pytest", passed),
            _tool("ruff", passed),
            _tool("mypy", passed),
        ],
        summary="ok" if passed else "failed",
    )


def _base_state(**overrides) -> AgentState:
    state: AgentState = {
        "task": "demo",
        "plan": None,
        "current_code": "code",
        "critic_feedback": [],
        "verification_result": None,
        "iteration": 0,
        "status": "reviewing",
        "trace": [],
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


def test_route_after_verifier_continues_to_critic_when_passed():
    state = _base_state(verification_result=_verification(True))
    assert route_after_verifier(state) == "critic"


def test_route_after_verifier_revises_when_failed_under_iteration_cap():
    state = _base_state(
        iteration=1,
        verification_result=_verification(False),
    )
    assert route_after_verifier(state) == "revise"


def test_route_after_verifier_fails_when_failed_at_iteration_cap():
    state = _base_state(
        iteration=3,
        verification_result=_verification(False),
    )
    assert route_after_verifier(state) == "failed"

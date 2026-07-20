from hialt.agents.coder import CoderAgent
from hialt.agents.critic import CriticAgent
from hialt.agents.planner import PlannerAgent
from hialt.providers.base import StubProvider
from hialt.state import CriticIssue, ExecutionPlan


def test_planner_agent_returns_execution_plan():
    agent = PlannerAgent(StubProvider())
    plan = agent.plan("build a CLI")
    assert isinstance(plan, ExecutionPlan)
    assert "build a CLI" in plan.objective
    assert isinstance(plan.assumptions, list)
    assert isinstance(plan.implementation_steps, list)
    assert isinstance(plan.files_affected, list)
    assert isinstance(plan.acceptance_criteria, list)


def test_coder_agent_returns_code_string():
    agent = CoderAgent(StubProvider())
    plan = ExecutionPlan(
        objective="build a CLI",
        assumptions=[],
        implementation_steps=[],
        files_affected=[],
        acceptance_criteria=[],
    )
    code = agent.code(plan, feedback=[])
    assert isinstance(code, str)
    assert "build a CLI" in code


def test_critic_agent_returns_issue_list():
    agent = CriticAgent(StubProvider())
    plan = ExecutionPlan(
        objective="build a CLI",
        assumptions=[],
        implementation_steps=[],
        files_affected=[],
        acceptance_criteria=[],
    )
    issues = agent.review(plan, code="print('hi')")
    assert isinstance(issues, list)
    assert all(isinstance(issue, CriticIssue) for issue in issues)

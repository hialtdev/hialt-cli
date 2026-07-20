import json

from hialt.agents.critic import CriticAgent
from hialt.errors import critic_issue_parse_failure, failure_envelope
from hialt.providers.base import StubProvider
from hialt.state import CriticIssue


def _agent() -> CriticAgent:
    return CriticAgent(StubProvider())


def _valid_issue_dict(**overrides) -> dict:
    base = {
        "description": "missing error handling",
        "severity": "minor",
        "category": "reliability",
        "confidence": 0.8,
        "recommendation": "add a try/except",
        "location": "main.py:10",
    }
    base.update(overrides)
    return base


def test_parse_valid_json_array():
    raw = json.dumps(
        [
            _valid_issue_dict(description="a"),
            _valid_issue_dict(description="b", severity="major"),
        ]
    )
    issues = _agent()._parse_response(raw)
    assert len(issues) == 2
    assert all(isinstance(i, CriticIssue) for i in issues)
    assert all(i.category != "parse_error" for i in issues)
    assert issues[0].description == "a"
    assert issues[1].severity == "major"


def test_parse_json_with_llm_mistakes():
    raw = """Here are my findings:
    [
      {
        'description': 'leaky abstraction',
        'severity': 'major',
        'category': 'design',
        'confidence': 0.7,
        'recommendation': 'introduce an interface',
        'location': null,
      },
    ]
    Hope that helps!
    """
    issues = _agent()._parse_response(raw)
    assert len(issues) == 1
    assert issues[0].category != "parse_error"
    assert issues[0].description == "leaky abstraction"
    assert issues[0].severity == "major"


def test_parse_one_invalid_item_becomes_fallback():
    raw = json.dumps(
        [
            _valid_issue_dict(description="ok item"),
            _valid_issue_dict(description="bad severity", severity="critical"),
            _valid_issue_dict(description="also ok", severity="blocking"),
        ]
    )
    issues = _agent()._parse_response(raw)
    assert len(issues) == 3
    assert issues[0].description == "ok item"
    assert issues[0].category != "parse_error"
    assert issues[1].category == "parse_error"
    assert issues[1].severity == "major"
    assert issues[1].confidence == 0.0
    assert issues[1].location is None
    assert "critical" in issues[1].description or "bad severity" in issues[1].description
    assert issues[2].description == "also ok"
    assert issues[2].severity == "blocking"


def test_parse_garbage_returns_single_fallback():
    issues = _agent()._parse_response("this is not json at all!!! @@@")
    assert len(issues) == 1
    assert issues[0].category == "parse_error"
    assert issues[0].severity == "major"
    assert issues[0].confidence == 0.0
    assert "this is not json" in issues[0].description


def test_parse_empty_array_means_no_issues():
    issues = _agent()._parse_response("[]")
    assert issues == []


def test_failure_envelope_shape():
    result = failure_envelope("error", "something broke", {"code": 1})
    assert result == {
        "status": "error",
        "message": "something broke",
        "detail": {"code": 1},
    }
    assert failure_envelope("ok", "fine")["detail"] == {}


def test_critic_issue_parse_failure_shape():
    raw = "x" * 600
    result = critic_issue_parse_failure(raw)
    assert result["status"] == "parse_error"
    assert result["message"] == "critic response could not be parsed"
    assert result["detail"]["raw"] == raw[:500]
    assert len(result["detail"]["raw"]) == 500

import logging
import operator
from typing import Annotated, Literal, TypedDict

from pydantic import BaseModel, Field
from hialt.execution_trace import TraceEntry

logger = logging.getLogger(__name__)


__all__ = [
    "AgentState",
    "CriticIssue",
    "ExecutionPlan",
    "ToolResult",
    "TraceEntry",
    "VerificationResult",
]

__all__ = [
    "AgentState",
    "CriticIssue",
    "ExecutionPlan",
    "ToolResult",
    "VerificationResult",
]


class CriticIssue(BaseModel):
    """Represent one validated critique finding used for routing decisions."""
    description: str
    severity: Literal["minor", "major", "blocking"]
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    recommendation: str
    location: str | None = None


class ExecutionPlan(BaseModel):
    """Carry the planner's structured handoff to coding and critique roles."""
    objective: str
    assumptions: list[str]
    implementation_steps: list[str]
    files_affected: list[str]
    acceptance_criteria: list[str]


class ToolResult(BaseModel):
    """Capture deterministic command evidence without raising expected failures."""
    tool: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float


class VerificationResult(BaseModel):
    """Summarize the verifier's objective result across tool executions."""
    passed: bool
    results: list[ToolResult]
    summary: str


class AgentState(TypedDict):
    """Define workflow-owned state shared and updated by LangGraph nodes."""
    task: str
    plan: ExecutionPlan | None
    current_code: str
    critic_feedback: list[CriticIssue]
    verification_result: VerificationResult | None
    iteration: int
    status: Literal[
        "planning",
        "coding",
        "verifying",
        "reviewing",
        "approved",
        "failed",
    ]
    execution_trace: Annotated[list[TraceEntry], operator.add]

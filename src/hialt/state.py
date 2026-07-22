import logging
import operator
from typing import Annotated, Literal, TypedDict

from pydantic import BaseModel, Field

from hialt.execution_trace import TraceEntry
from hialt.execution_trace import TraceEvent as EventType

logger = logging.getLogger(__name__)

# Deprecated compatibility aliases. New code uses TraceEntry and TraceEvent.
AgentEvent = TraceEntry

__all__ = [
    "AgentEvent",
    "AgentState",
    "CriticIssue",
    "EventType",
    "ExecutionPlan",
    "ToolResult",
    "VerificationResult",
]


class CriticIssue(BaseModel):
    description: str
    severity: Literal["minor", "major", "blocking"]
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    recommendation: str
    location: str | None = None


class ExecutionPlan(BaseModel):
    objective: str
    assumptions: list[str]
    implementation_steps: list[str]
    files_affected: list[str]
    acceptance_criteria: list[str]


class ToolResult(BaseModel):
    tool: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float


class VerificationResult(BaseModel):
    passed: bool
    results: list[ToolResult]
    summary: str


class AgentState(TypedDict):
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
    # Deprecated state key retained for callers migrating from the event subsystem.
    trace: Annotated[list[TraceEntry], operator.add]

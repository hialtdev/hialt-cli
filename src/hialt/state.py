from datetime import datetime
from enum import Enum
from typing import Annotated, Any, List, Literal, TypedDict
import operator

from pydantic import BaseModel, ConfigDict, Field


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


class EventType(str, Enum):
    GRAPH_STARTED = "graph_started"
    PLANNING_STARTED = "planning_started"
    PLANNING_COMPLETED = "planning_completed"
    CODING_STARTED = "coding_started"
    CODING_COMPLETED = "coding_completed"
    TOOL_REQUESTED = "tool_requested"
    TOOL_COMPLETED = "tool_completed"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_COMPLETED = "verification_completed"
    CRITIQUE_STARTED = "critique_started"
    CRITIQUE_COMPLETED = "critique_completed"
    REVISION_REQUESTED = "revision_requested"
    ITERATION_INCREMENTED = "iteration_incremented"
    APPROVED = "approved"
    FAILED = "failed"


class AgentEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    node: str
    event_type: EventType
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentState(TypedDict):
    task: str
    plan: ExecutionPlan | None
    current_code: str
    critic_feedback: List[CriticIssue]
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
    trace: Annotated[list[AgentEvent], operator.add]

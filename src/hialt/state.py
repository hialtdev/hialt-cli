from typing import List, Literal, TypedDict

from pydantic import BaseModel, Field


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


class AgentState(TypedDict):
    task: str
    plan: ExecutionPlan | None
    current_code: str
    critic_feedback: List[CriticIssue]
    iteration: int
    status: Literal["planning", "coding", "reviewing", "approved", "failed"]

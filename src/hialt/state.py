from typing import List, Literal, TypedDict

from pydantic import BaseModel


class CriticIssue(BaseModel):
    description: str
    severity: Literal["minor", "major", "blocking"]


class AgentState(TypedDict):
    task: str
    plan: str
    current_code: str
    critic_feedback: List[CriticIssue]
    iteration: int
    status: Literal["planning", "coding", "reviewing", "approved", "failed"]

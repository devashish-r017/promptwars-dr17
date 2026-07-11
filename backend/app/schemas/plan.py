"""Pydantic schemas for preparedness plan."""

from pydantic import BaseModel


class PlanItem(BaseModel):
    category: str  # e.g., "Home Safety", "Emergency Kit", "Health"
    description: str
    priority: str  # "high", "medium", "low"
    personalized_note: str | None = None  # Why this is relevant for this profile


class PlanPhase(BaseModel):
    phase: str  # "before", "during", "after"
    title: str
    items: list[PlanItem]


class PrepPlanResponse(BaseModel):
    phases: list[PlanPhase]
    current_phase: str  # "before", "during", "after"
    profile_summary: str  # Brief summary of how the plan is personalized

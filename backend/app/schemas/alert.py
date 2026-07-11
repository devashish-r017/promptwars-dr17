"""Pydantic schemas for alerts."""

from datetime import datetime
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    severity: str = Field(..., pattern="^(info|warning|critical)$")
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    affected_area: str
    recommended_actions: list[str] = []


class AlertResponse(BaseModel):
    id: int
    severity: str
    title: str
    description: str
    affected_area: str
    recommended_actions: list[str]
    is_active: bool
    created_at: datetime
    expires_at: datetime | None

    model_config = {"from_attributes": True}

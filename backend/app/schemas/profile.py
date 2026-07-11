"""Pydantic schemas for user profile CRUD."""

from datetime import datetime
from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    """Pydantic schema representing parameters needed to create a new user profile."""
    name: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=50)
    family_size: int = Field(default=1, ge=1, le=50)
    has_elderly: bool = False
    has_children: bool = False
    has_pets: bool = False
    dwelling_type: str = Field(
        default="independent_house",
        pattern="^(ground_floor|high_rise|basement|independent_house|kaccha_house)$",
    )
    health_conditions: str | None = None
    has_vehicle: bool = False
    near_water_body: bool = False
    preferred_language: str = Field(default="en", pattern="^(en|hi)$")


class ProfileUpdate(BaseModel):
    """Pydantic schema representing optional parameters to update an existing user profile."""
    name: str | None = None
    city: str | None = None
    family_size: int | None = Field(default=None, ge=1, le=50)
    has_elderly: bool | None = None
    has_children: bool | None = None
    has_pets: bool | None = None
    dwelling_type: str | None = None
    health_conditions: str | None = None
    has_vehicle: bool | None = None
    near_water_body: bool | None = None
    preferred_language: str | None = None


class ProfileResponse(BaseModel):
    """Pydantic schema representing complete details of a user profile returned in responses."""
    id: int
    name: str
    city: str
    family_size: int
    has_elderly: bool
    has_children: bool
    has_pets: bool
    dwelling_type: str
    health_conditions: str | None
    has_vehicle: bool
    near_water_body: bool
    preferred_language: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

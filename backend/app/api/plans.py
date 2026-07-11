"""Preparedness plan routes — AI-generated personalized plans."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_profile import UserProfile
from app.schemas.plan import PrepPlanResponse
from app.services import ai_service, cache_service, weather_service

router = APIRouter(prefix="/api/plans", tags=["plans"])


def _profile_to_dict(p: UserProfile) -> dict:
    """Convert profile ORM object to dict for AI prompt."""
    return {
        "name": p.name,
        "city": p.city,
        "family_size": p.family_size,
        "has_elderly": p.has_elderly,
        "has_children": p.has_children,
        "has_pets": p.has_pets,
        "dwelling_type": p.dwelling_type,
        "health_conditions": p.health_conditions,
        "has_vehicle": p.has_vehicle,
        "near_water_body": p.near_water_body,
    }


@router.get("/{profile_id}", response_model=PrepPlanResponse)
async def get_plan(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    weather = await weather_service.get_weather(profile.city)
    weather_hash = weather_service.get_weather_hash(weather)

    # Check cache
    cached = cache_service.get_cached(
        db, profile_id, "preparedness_plan", weather_hash, profile.preferred_language
    )
    if cached and "error" not in cached:
        return PrepPlanResponse(**cached)

    # Generate fresh
    plan_data = await ai_service.generate_plan(
        _profile_to_dict(profile),
        weather.model_dump(),
        profile.preferred_language,
    )

    if "error" not in plan_data:
        cache_service.set_cached(
            db, profile_id, "preparedness_plan", weather_hash,
            profile.preferred_language, plan_data, ttl_seconds=3600,
        )

    return PrepPlanResponse(**plan_data)


@router.post("/{profile_id}/regenerate", response_model=PrepPlanResponse)
async def regenerate_plan(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Invalidate existing cache
    cache_service.invalidate(db, profile_id, "preparedness_plan")

    weather = await weather_service.get_weather(profile.city)
    weather_hash = weather_service.get_weather_hash(weather)

    plan_data = await ai_service.generate_plan(
        _profile_to_dict(profile),
        weather.model_dump(),
        profile.preferred_language,
    )

    if "error" not in plan_data:
        cache_service.set_cached(
            db, profile_id, "preparedness_plan", weather_hash,
            profile.preferred_language, plan_data, ttl_seconds=3600,
        )

    return PrepPlanResponse(**plan_data)

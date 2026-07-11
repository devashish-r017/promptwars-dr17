"""Preparedness plan routes — AI-generated personalized plans."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_profile import UserProfile
from app.schemas.plan import PrepPlanResponse
from app.services import ai_service, cache_service, weather_service

router = APIRouter(prefix="/api/plans", tags=["plans"])


async def _generate_and_cache_plan(
    db: Session,
    profile: UserProfile,
    weather,
    weather_hash: str,
) -> dict:
    """Generate a fresh plan and save to cache if no error."""
    plan_data = await ai_service.generate_plan(
        profile.to_dict(),
        weather.model_dump(),
        profile.preferred_language,
    )

    if "error" not in plan_data:
        cache_service.set_cached(
            db,
            profile.id,
            "preparedness_plan",
            weather_hash,
            profile.preferred_language,
            plan_data,
            ttl_seconds=3600,
        )

    return plan_data


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

    plan_data = await _generate_and_cache_plan(db, profile, weather, weather_hash)
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

    plan_data = await _generate_and_cache_plan(db, profile, weather, weather_hash)
    return PrepPlanResponse(**plan_data)


"""Dashboard routes — aggregated data for the main dashboard view."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_profile import UserProfile
from app.schemas.dashboard import DashboardResponse
from app.services import ai_service, alert_service, cache_service, weather_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/{profile_id}", response_model=DashboardResponse)
async def get_dashboard(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    weather = await weather_service.get_weather(profile.city)
    weather_hash = weather_service.get_weather_hash(weather)

    # Check cache for AI-generated parts
    cached = cache_service.get_cached(
        db, profile_id, "dashboard", weather_hash, profile.preferred_language
    )

    if cached and "error" not in cached:
        dashboard_ai = cached
    else:
        dashboard_ai = await ai_service.generate_dashboard(
            profile.to_dict(),
            weather.model_dump(),
            profile.preferred_language,
        )
        if "error" not in dashboard_ai:
            cache_service.set_cached(
                db, profile_id, "dashboard", weather_hash,
                profile.preferred_language, dashboard_ai, ttl_seconds=3600,
            )

    # Always fetch fresh alerts (not cached)
    recent_alerts = alert_service.get_active_alerts(db, profile.city)

    return DashboardResponse(
        weather=weather,
        risk_score=dashboard_ai.get("risk_score", {"score": 50, "level": "moderate", "explanation": "Unable to assess"}),
        checklist=dashboard_ai.get("checklist", {"items": []}),
        travel=dashboard_ai.get("travel", {"safety_rating": "caution", "summary": "Check conditions", "tips": []}),
        safety=dashboard_ai.get("safety", {"tips": []}),
        recent_alerts=recent_alerts,
    )

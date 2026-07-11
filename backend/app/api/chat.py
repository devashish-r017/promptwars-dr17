"""Chat routes — AI-powered contextual assistant."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_profile import UserProfile
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import ai_service, weather_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(data: ChatRequest, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == data.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    weather = await weather_service.get_weather(profile.city)

    profile_dict = {
        "name": profile.name,
        "city": profile.city,
        "family_size": profile.family_size,
        "has_elderly": profile.has_elderly,
        "has_children": profile.has_children,
        "has_pets": profile.has_pets,
        "dwelling_type": profile.dwelling_type,
        "health_conditions": profile.health_conditions,
        "has_vehicle": profile.has_vehicle,
        "near_water_body": profile.near_water_body,
    }

    history = [msg.model_dump() for msg in data.history]

    reply = await ai_service.chat_reply(
        profile_dict=profile_dict,
        weather_dict=weather.model_dump(),
        message=data.message,
        page_context=data.page_context,
        history=history,
        language=profile.preferred_language,
    )

    return ChatResponse(reply=reply)

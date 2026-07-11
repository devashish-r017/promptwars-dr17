"""Weather routes — get current weather, scenario override controls."""

from fastapi import APIRouter

from app.schemas.weather import WeatherDataResponse, WeatherOverrideRequest
from app.services import weather_service

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/{city}", response_model=WeatherDataResponse)
async def get_weather(city: str):
    return await weather_service.get_weather(city)


@router.post("/override")
def set_override(data: WeatherOverrideRequest):
    weather_service.set_override(data.scenario)
    return {"status": "ok", "scenario": data.scenario}


@router.delete("/override")
def clear_override():
    weather_service.clear_override()
    return {"status": "ok", "scenario": None}

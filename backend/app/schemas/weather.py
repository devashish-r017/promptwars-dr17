"""Pydantic schemas for weather data."""

from pydantic import BaseModel, Field


class WeatherDataResponse(BaseModel):
    """Pydantic schema representing structured weather conditions, risk levels, and monsoon phase info."""
    city: str
    temperature_c: float
    humidity_percent: float
    rainfall_mm: float
    wind_speed_kmh: float
    condition: str  # e.g., "Heavy Rain", "Thunderstorm", "Clear"
    flood_risk: str = Field(pattern="^(low|moderate|high|very_high)$")
    severity: str = Field(pattern="^(normal|watch|warning|critical)$")
    monsoon_phase: str = Field(pattern="^(pre_monsoon|active_monsoon|post_monsoon)$")
    source: str  # "override", "simulated", "live"


class WeatherOverrideRequest(BaseModel):
    """Pydantic schema for requesting a weather scenario simulation override."""
    scenario: str = Field(
        ...,
        pattern="^(normal|heavy_rain|flood_risk|cyclone_warning|post_monsoon_clear)$",
    )

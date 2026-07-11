"""Hybrid weather service — scenario override → simulated → live OpenWeatherMap."""

import hashlib
import json
import os
from typing import Any

import httpx
from fastapi import HTTPException

from app.schemas.weather import WeatherDataResponse

# ---------------------------------------------------------------------------
# In-memory scenario override (set via API, highest priority)
# ---------------------------------------------------------------------------
_current_override: dict[str, Any] | None = None


def set_override(scenario: str) -> None:
    global _current_override
    _current_override = _SCENARIOS.get(scenario)


def clear_override() -> None:
    global _current_override
    _current_override = None


def get_override() -> dict[str, Any] | None:
    return _current_override


HEAVY_RAIN = "Heavy Rain"
MODERATE_RAIN = "Moderate Rain"
LIGHT_RAIN = "Light Rain"


# ---------------------------------------------------------------------------
# Predefined weather scenarios for demo
# ---------------------------------------------------------------------------
_SCENARIOS: dict[str, dict[str, Any]] = {
    "normal": {
        "temperature_c": 30.0,
        "humidity_percent": 65.0,
        "rainfall_mm": 5.0,
        "wind_speed_kmh": 12.0,
        "condition": "Partly Cloudy",
        "flood_risk": "low",
        "severity": "normal",
        "monsoon_phase": "active_monsoon",
    },
    "heavy_rain": {
        "temperature_c": 26.0,
        "humidity_percent": 92.0,
        "rainfall_mm": 120.0,
        "wind_speed_kmh": 35.0,
        "condition": HEAVY_RAIN,
        "flood_risk": "high",
        "severity": "warning",
        "monsoon_phase": "active_monsoon",
    },
    "flood_risk": {
        "temperature_c": 25.0,
        "humidity_percent": 96.0,
        "rainfall_mm": 200.0,
        "wind_speed_kmh": 45.0,
        "condition": "Torrential Rain & Flooding",
        "flood_risk": "very_high",
        "severity": "critical",
        "monsoon_phase": "active_monsoon",
    },
    "cyclone_warning": {
        "temperature_c": 27.0,
        "humidity_percent": 88.0,
        "rainfall_mm": 150.0,
        "wind_speed_kmh": 90.0,
        "condition": "Cyclonic Storm",
        "flood_risk": "very_high",
        "severity": "critical",
        "monsoon_phase": "active_monsoon",
    },
    "post_monsoon_clear": {
        "temperature_c": 32.0,
        "humidity_percent": 55.0,
        "rainfall_mm": 0.0,
        "wind_speed_kmh": 8.0,
        "condition": "Clear Sky",
        "flood_risk": "low",
        "severity": "normal",
        "monsoon_phase": "post_monsoon",
    },
}

# ---------------------------------------------------------------------------
# Live Open-Meteo integration (free, no key required)
# ---------------------------------------------------------------------------

_WMO_SEVERITY_MAP = {
    0: ("normal", "low", "Clear Sky"),
    1: ("normal", "low", "Mainly Clear"),
    2: ("normal", "low", "Partly Cloudy"),
    3: ("normal", "low", "Overcast"),
    45: ("normal", "low", "Fog"),
    48: ("normal", "low", "Fog"),
    51: ("normal", "low", "Light Drizzle"),
    53: ("normal", "low", "Moderate Drizzle"),
    55: ("normal", "low", "Heavy Drizzle"),
    56: ("normal", "low", "Light Freezing Drizzle"),
    57: ("normal", "low", "Heavy Freezing Drizzle"),
    61: ("normal", "low", "Light Rain"),
    63: ("watch", "moderate", "Moderate Rain"),
    65: ("warning", "high", "Heavy Rain"),
    66: ("watch", "moderate", "Light Freezing Rain"),
    67: ("warning", "high", "Heavy Freezing Rain"),
    71: ("watch", "low", "Light Snow"),
    73: ("watch", "low", "Moderate Snow"),
    75: ("warning", "low", "Heavy Snow"),
    77: ("watch", "low", "Snow Grains"),
    80: ("normal", "low", "Light Rain Showers"),
    81: ("watch", "moderate", "Moderate Rain Showers"),
    82: ("warning", "high", "Violent Rain Showers"),
    85: ("watch", "low", "Light Snow Showers"),
    86: ("warning", "low", "Heavy Snow Showers"),
    95: ("warning", "high", "Thunderstorm"),
    96: ("critical", "very_high", "Thunderstorm with Slight Hail"),
    99: ("critical", "very_high", "Thunderstorm with Heavy Hail"),
}


async def _fetch_open_meteo(city: str) -> dict[str, Any] | None:
    """Fetch live weather from Open-Meteo API. Returns None on failure."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Step 1: Geocode city name to get lat/lon
            resp = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 5, "language": "en", "format": "json"},
            )
            if resp.status_code != 200:
                return None
            
            geo_data = resp.json()
            results = geo_data.get("results")
            if not results:
                return None
            
            # Find the first result in India, otherwise use the first result
            location = None
            for res in results:
                if res.get("country_code") == "IN" or res.get("country") == "India":
                    location = res
                    break
            if not location:
                location = results[0]
                
            lat = location["latitude"]
            lon = location["longitude"]
            
            # Step 2: Fetch current weather for the coordinates
            weather_resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
                    "wind_speed_unit": "kmh"
                }
            )
            if weather_resp.status_code != 200:
                return None
                
            weather_data = weather_resp.json()
            current = weather_data.get("current")
            if not current:
                return None
            
            wcode = current.get("weather_code", 0)
            severity, flood_risk, condition = _WMO_SEVERITY_MAP.get(wcode, ("normal", "low", "Clear Sky"))
            
            # Rain overrides
            rain_mm = current.get("precipitation", 0.0) or 0.0
            if rain_mm > 100:
                severity = "critical"
                flood_risk = "very_high"
            elif rain_mm > 50:
                severity = "warning"
                flood_risk = "high"
                
            return {
                "temperature_c": round(current.get("temperature_2m", 0.0), 1),
                "humidity_percent": float(current.get("relative_humidity_2m", 0.0)),
                "rainfall_mm": round(rain_mm, 1),
                "wind_speed_kmh": round(current.get("wind_speed_10m", 0.0), 1),
                "condition": condition,
                "flood_risk": flood_risk,
                "severity": severity,
                "monsoon_phase": "active_monsoon",
            }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Live OpenWeatherMap integration
# ---------------------------------------------------------------------------

_OWM_SEVERITY_MAP = {
    "Thunderstorm": ("warning", "high"),
    "Drizzle": ("normal", "low"),
    "Rain": ("watch", "moderate"),
    "Snow": ("watch", "low"),
    "Clear": ("normal", "low"),
    "Clouds": ("normal", "low"),
}


async def _fetch_live(city: str) -> dict[str, Any] | None:
    """Fetch live weather from OpenWeatherMap. Returns None on failure."""
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "")
    if not api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": f"{city},IN", "appid": api_key, "units": "metric"},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()

        main_weather = data.get("weather", [{}])[0].get("main", "Clear")
        severity, flood_risk = _OWM_SEVERITY_MAP.get(main_weather, ("normal", "low"))

        rain_mm = 0.0
        rain_dict = data.get("rain")
        if isinstance(rain_dict, dict):
            rain_mm = rain_dict.get("1h", 0.0) or rain_dict.get("3h", 0.0) or 0.0

        if rain_mm > 100:
            severity = "critical"
            flood_risk = "very_high"
        elif rain_mm > 50:
            severity = "warning"
            flood_risk = "high"

        return {
            "temperature_c": round(data["main"]["temp"], 1),
            "humidity_percent": float(data["main"]["humidity"]),
            "rainfall_mm": round(rain_mm, 1),
            "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 1),
            "condition": data["weather"][0]["description"].title(),
            "flood_risk": flood_risk,
            "severity": severity,
            "monsoon_phase": "active_monsoon",
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_weather(city: str) -> WeatherDataResponse:
    """Resolve weather via priority: override → live (OpenWeatherMap) → live (Open-Meteo)."""

    # Tier 1: Scenario override
    override = get_override()
    if override is not None:
        return WeatherDataResponse(city=city, source="override", **override)

    # Tier 2: Try live API (OpenWeatherMap if key configured)
    live = await _fetch_live(city)
    if live is not None:
        return WeatherDataResponse(city=city, source="live", **live)

    # Tier 3: Try live API (Open-Meteo - keyless fallback)
    live_om = await _fetch_open_meteo(city)
    if live_om is not None:
        return WeatherDataResponse(city=city, source="live", **live_om)

    # If all options fail, raise service unavailable error
    raise HTTPException(
        status_code=503,
        detail=f"Real-time weather data for '{city}' is currently unavailable."
    )


def get_weather_hash(weather: WeatherDataResponse) -> str:
    """Deterministic hash for cache invalidation."""
    key_fields = {
        "severity": weather.severity,
        "flood_risk": weather.flood_risk,
        "condition": weather.condition,
        "monsoon_phase": weather.monsoon_phase,
    }
    return hashlib.sha256(json.dumps(key_fields, sort_keys=True).encode()).hexdigest()[:16]

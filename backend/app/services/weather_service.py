"""Hybrid weather service — scenario override → simulated → live OpenWeatherMap."""

import hashlib
import json
import os
import random
from typing import Any

import httpx

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
        "condition": "Heavy Rain",
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
# Per-city simulated baselines (realistic monsoon profiles for Indian cities)
# ---------------------------------------------------------------------------
_CITY_BASELINES: dict[str, dict[str, Any]] = {
    "Mumbai": {
        "temperature_c": 28.0, "humidity_percent": 88.0, "rainfall_mm": 80.0,
        "wind_speed_kmh": 25.0, "condition": "Heavy Rain",
        "flood_risk": "high", "severity": "warning", "monsoon_phase": "active_monsoon",
    },
    "Delhi": {
        "temperature_c": 34.0, "humidity_percent": 72.0, "rainfall_mm": 30.0,
        "wind_speed_kmh": 15.0, "condition": "Moderate Rain",
        "flood_risk": "moderate", "severity": "watch", "monsoon_phase": "active_monsoon",
    },
    "Chennai": {
        "temperature_c": 32.0, "humidity_percent": 78.0, "rainfall_mm": 20.0,
        "wind_speed_kmh": 18.0, "condition": "Light Rain",
        "flood_risk": "moderate", "severity": "normal", "monsoon_phase": "pre_monsoon",
    },
    "Kolkata": {
        "temperature_c": 30.0, "humidity_percent": 85.0, "rainfall_mm": 60.0,
        "wind_speed_kmh": 20.0, "condition": "Rain & Thunderstorm",
        "flood_risk": "high", "severity": "warning", "monsoon_phase": "active_monsoon",
    },
    "Bengaluru": {
        "temperature_c": 24.0, "humidity_percent": 70.0, "rainfall_mm": 25.0,
        "wind_speed_kmh": 12.0, "condition": "Light Rain",
        "flood_risk": "low", "severity": "normal", "monsoon_phase": "active_monsoon",
    },
    "Hyderabad": {
        "temperature_c": 29.0, "humidity_percent": 75.0, "rainfall_mm": 35.0,
        "wind_speed_kmh": 16.0, "condition": "Moderate Rain",
        "flood_risk": "moderate", "severity": "watch", "monsoon_phase": "active_monsoon",
    },
    "Pune": {
        "temperature_c": 25.0, "humidity_percent": 82.0, "rainfall_mm": 55.0,
        "wind_speed_kmh": 22.0, "condition": "Heavy Rain",
        "flood_risk": "moderate", "severity": "watch", "monsoon_phase": "active_monsoon",
    },
    "Jaipur": {
        "temperature_c": 35.0, "humidity_percent": 60.0, "rainfall_mm": 15.0,
        "wind_speed_kmh": 10.0, "condition": "Partly Cloudy",
        "flood_risk": "low", "severity": "normal", "monsoon_phase": "pre_monsoon",
    },
    "Ahmedabad": {
        "temperature_c": 33.0, "humidity_percent": 68.0, "rainfall_mm": 25.0,
        "wind_speed_kmh": 14.0, "condition": "Light Rain",
        "flood_risk": "low", "severity": "normal", "monsoon_phase": "active_monsoon",
    },
    "Lucknow": {
        "temperature_c": 33.0, "humidity_percent": 74.0, "rainfall_mm": 28.0,
        "wind_speed_kmh": 13.0, "condition": "Moderate Rain",
        "flood_risk": "moderate", "severity": "watch", "monsoon_phase": "active_monsoon",
    },
}

# Fallback for unlisted cities
_DEFAULT_BASELINE: dict[str, Any] = {
    "temperature_c": 30.0, "humidity_percent": 75.0, "rainfall_mm": 40.0,
    "wind_speed_kmh": 15.0, "condition": "Moderate Rain",
    "flood_risk": "moderate", "severity": "watch", "monsoon_phase": "active_monsoon",
}


def _simulate(city: str) -> dict[str, Any]:
    """Return simulated weather with slight randomization."""
    base = _CITY_BASELINES.get(city, _DEFAULT_BASELINE).copy()
    # Add realistic variance
    base["temperature_c"] += random.uniform(-2, 2)
    base["humidity_percent"] = min(100, max(30, base["humidity_percent"] + random.uniform(-5, 5)))
    base["rainfall_mm"] = max(0, base["rainfall_mm"] + random.uniform(-10, 15))
    base["wind_speed_kmh"] = max(0, base["wind_speed_kmh"] + random.uniform(-5, 5))
    # Round values
    for key in ("temperature_c", "humidity_percent", "rainfall_mm", "wind_speed_kmh"):
        base[key] = round(base[key], 1)
    return base


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

        rain_mm = data.get("rain", {}).get("1h", 0) or data.get("rain", {}).get("3h", 0)
        if rain_mm > 100:
            severity = "critical"
            flood_risk = "very_high"
        elif rain_mm > 50:
            severity = "warning"
            flood_risk = "high"

        return {
            "temperature_c": round(data["main"]["temp"], 1),
            "humidity_percent": data["main"]["humidity"],
            "rainfall_mm": round(rain_mm, 1),
            "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 1),
            "condition": data["weather"][0]["description"].title(),
            "flood_risk": flood_risk,
            "severity": severity,
            "monsoon_phase": "active_monsoon",  # Simplified
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_weather(city: str) -> WeatherDataResponse:
    """Resolve weather via three-tier priority: override → simulated → live."""

    # Tier 1: Scenario override
    override = get_override()
    if override is not None:
        return WeatherDataResponse(city=city, source="override", **override)

    # Tier 2: Try live API (if key configured)
    live = await _fetch_live(city)
    if live is not None:
        return WeatherDataResponse(city=city, source="live", **live)

    # Tier 3: Simulated fallback (always works)
    sim = _simulate(city)
    return WeatherDataResponse(city=city, source="simulated", **sim)


def get_weather_hash(weather: WeatherDataResponse) -> str:
    """Deterministic hash for cache invalidation."""
    key_fields = {
        "severity": weather.severity,
        "flood_risk": weather.flood_risk,
        "condition": weather.condition,
        "monsoon_phase": weather.monsoon_phase,
    }
    return hashlib.sha256(json.dumps(key_fields, sort_keys=True).encode()).hexdigest()[:16]

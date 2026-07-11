import asyncio
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.cached_response import CachedResponse
from app.schemas.weather import WeatherDataResponse
from app.services import cache_service, weather_service, alert_service


# ===========================================================================
# Cache Service Tests
# ===========================================================================

def test_cache_set_and_get(db: Session):
    profile_id = 1
    content_type = "preparedness_plan"
    weather_hash = "abc123weather"
    language = "en"
    response_data = {"test_key": "test_value"}

    # Initially cache is empty
    assert cache_service.get_cached(db, profile_id, content_type, weather_hash, language) is None

    # Set cache
    cache_service.set_cached(db, profile_id, content_type, weather_hash, language, response_data)

    # Retrieve cache
    cached = cache_service.get_cached(db, profile_id, content_type, weather_hash, language)
    assert cached == response_data


def test_cache_ttl_expiration(db: Session):
    profile_id = 1
    content_type = "preparedness_plan"
    weather_hash = "abc123weather"
    language = "en"
    response_data = {"test_key": "test_value"}

    # Set cache with short TTL (e.g. -1 second to simulate expiration)
    cache_service.set_cached(
        db, profile_id, content_type, weather_hash, language, response_data, ttl_seconds=-1
    )

    # Cache should be expired and return None
    cached = cache_service.get_cached(db, profile_id, content_type, weather_hash, language)
    assert cached is None

    # Database row should have been cleaned up
    entry = db.query(CachedResponse).first()
    assert entry is None


def test_cache_invalidation(db: Session):
    profile_id = 1
    weather_hash = "abc123weather"
    response_data = {"data": "test"}

    # Set two different cache items
    cache_service.set_cached(db, profile_id, "plan", weather_hash, "en", response_data)
    cache_service.set_cached(db, profile_id, "dashboard", weather_hash, "en", response_data)
    cache_service.set_cached(db, 2, "plan", weather_hash, "en", response_data)  # Different profile

    # Invalidate plan only for profile 1
    count = cache_service.invalidate(db, profile_id, "plan")
    assert count == 1
    assert cache_service.get_cached(db, profile_id, "plan", weather_hash, "en") is None
    assert cache_service.get_cached(db, profile_id, "dashboard", weather_hash, "en") is not None
    assert cache_service.get_cached(db, 2, "plan", weather_hash, "en") is not None

    # Invalidate all for profile 1
    cache_service.invalidate(db, profile_id)
    assert cache_service.get_cached(db, profile_id, "dashboard", weather_hash, "en") is None
    assert cache_service.get_cached(db, 2, "plan", weather_hash, "en") is not None


# ===========================================================================
# Weather Service Tests
# ===========================================================================

def test_weather_override_controls():
    # Clear override to ensure clean state
    weather_service.clear_override()
    assert weather_service.get_override() is None

    # Set override
    weather_service.set_override("heavy_rain")
    override = weather_service.get_override()
    assert override is not None
    assert override["condition"] == "Heavy Rain"
    assert override["severity"] == "warning"

    # Set invalid override should be ignored or return None
    weather_service.set_override("invalid_scenario_name")
    assert weather_service.get_override() is None

    # Clear override
    weather_service.clear_override()
    assert weather_service.get_override() is None


@pytest.mark.asyncio
async def test_weather_resolution_override():
    weather_service.set_override("flood_risk")
    try:
        weather = await weather_service.get_weather("Mumbai")
        assert weather.city == "Mumbai"
        assert weather.source == "override"
        assert weather.condition == "Torrential Rain & Flooding"
        assert weather.severity == "critical"
        assert weather.flood_risk == "very_high"
    finally:
        weather_service.clear_override()


@pytest.mark.asyncio
async def test_weather_resolution_simulated_fallback():
    weather_service.clear_override()
    
    # 1. Test baseline city
    weather = await weather_service.get_weather("Mumbai")
    assert weather.city == "Mumbai"
    assert weather.source == "simulated"
    # Mumbai baseline is warning/high
    assert weather.flood_risk in ("moderate", "high", "very_high")
    
    # 2. Test unregistered city
    weather_unregistered = await weather_service.get_weather("NonExistentCity")
    assert weather_unregistered.city == "NonExistentCity"
    assert weather_unregistered.source == "simulated"
    assert weather_unregistered.condition == "Moderate Rain"


@pytest.mark.asyncio
async def test_weather_resolution_live_fetching(monkeypatch):
    weather_service.clear_override()
    monkeypatch.setenv("OPENWEATHERMAP_API_KEY", "mocked_key")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "main": {"temp": 29.5, "humidity": 85},
        "wind": {"speed": 10.0},  # 10 m/s = 36 km/h
        "weather": [{"main": "Rain", "description": "heavy intensity rain"}],
        "rain": {"1h": 55.0}
    }

    # Patch httpx.AsyncClient.get inside weather_service
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        weather = await weather_service.get_weather("Kolkata")
        assert weather.city == "Kolkata"
        assert weather.source == "live"
        assert weather.temperature_c == 29.5
        assert weather.humidity_percent == 85
        assert weather.wind_speed_kmh == 36.0
        assert weather.condition == "Heavy Intensity Rain"
        assert weather.severity == "warning"
        assert weather.flood_risk == "high"


def test_weather_hash():
    w1 = WeatherDataResponse(
        city="Mumbai", source="simulated", temperature_c=28.0, humidity_percent=80.0,
        rainfall_mm=50.0, wind_speed_kmh=15.0, condition="Rainy", flood_risk="high",
        severity="warning", monsoon_phase="active_monsoon"
    )
    w2 = WeatherDataResponse(
        city="Delhi", source="simulated", temperature_c=32.0, humidity_percent=70.0,
        rainfall_mm=20.0, wind_speed_kmh=10.0, condition="Rainy", flood_risk="high",
        severity="warning", monsoon_phase="active_monsoon"
    )
    # Even though temperature, rainfall etc. differ, key hash fields match
    assert weather_service.get_weather_hash(w1) == weather_service.get_weather_hash(w2)


# ===========================================================================
# Alert Service Tests
# ===========================================================================

def test_alert_creation_and_retrieval(db: Session):
    # Setup database alerts
    alert_service.create_alert(
        db=db,
        severity="warning",
        title="Heavy Waterlogging",
        description="Waterlogging on main highway",
        affected_area="Mumbai",
        actions=["Avoid the highway", "Use rail transport"],
        expires_minutes=15
    )
    
    # Retrieve alerts
    active = alert_service.get_active_alerts(db, "Mumbai")
    assert len(active) == 1
    assert active[0].title == "Heavy Waterlogging"
    assert active[0].severity == "warning"
    assert active[0].recommended_actions == ["Avoid the highway", "Use rail transport"]

    # Check that another city gets empty list
    assert len(alert_service.get_active_alerts(db, "Delhi")) == 0


def test_alert_expiry_logic(db: Session):
    # Create an alert that expired 5 minutes ago
    expired_alert = Alert(
        severity="critical",
        title="Immediate Flood Risk",
        description="Flooding near river",
        affected_area="Chennai",
        recommended_actions=json.dumps(["Evacuate"]),
        is_active=True,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    db.add(expired_alert)
    db.commit()

    # Query active alerts — it should notice the expiration, deactivate it, and return empty list
    active = alert_service.get_active_alerts(db, "Chennai")
    assert len(active) == 0

    # Ensure it was updated in the DB to inactive
    db.refresh(expired_alert)
    assert expired_alert.is_active is False


@pytest.mark.asyncio
async def test_demo_timeline_execution(monkeypatch, db):
    # Mock asyncio.sleep to complete instantly so the test runs immediately
    async def mock_sleep(seconds):
        pass
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    # We need a db_factory that returns our clean_db session
    def db_factory():
        return db

    # Start timeline
    await alert_service.start_demo_timeline("Mumbai", db_factory)

    # Let the background task run to completion (since sleep is 0, it finishes instantly)
    # We yield control to the event loop so the task runs
    await asyncio.sleep(0.01)
    if alert_service._demo_task:
        await alert_service._demo_task

    # Verify that all 5 alerts were created in the DB
    active_alerts = alert_service.get_active_alerts(db, "Mumbai")
    assert len(active_alerts) == 5
    # Order should be descending by created_at, first timeline item is "Rain Watch Issued" (created last? no, created first but all at same time. Let's check titles)
    titles = [a.title for a in active_alerts]
    assert "🌧️ Rain Watch Issued" in titles
    assert "⚠️ Heavy Rain Warning" in titles
    assert "🚨 Flood Alert — Low-Lying Areas" in titles
    assert "🆘 Evacuation Advisory" in titles
    assert "✅ Situation Stabilizing" in titles


@pytest.mark.asyncio
async def test_demo_timeline_cancellation(monkeypatch, db):
    # Keep reference to original asyncio.sleep to avoid infinite recursion
    original_sleep = asyncio.sleep

    # Mock asyncio.sleep to hang indefinitely for step 2 (so we can test cancelling it)
    async def mock_sleep(seconds):
        if seconds > 0:
            await original_sleep(9999)  # Stay suspended
        else:
            pass  # Step 1 delay is 0, let it run

    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    def db_factory():
        return db

    await alert_service.start_demo_timeline("Delhi", db_factory)
    await original_sleep(0.01)  # Let step 1 run

    # Verify step 1 alert created
    assert len(alert_service.get_active_alerts(db, "Delhi")) == 1

    # Now cancel the demo
    await alert_service.stop_demo_timeline()
    assert alert_service._demo_task is None

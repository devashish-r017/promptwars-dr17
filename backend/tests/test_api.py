"""Integration tests for all StormShield API routes."""

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from app.models.user_profile import UserProfile
from app.models.cached_response import CachedResponse
from app.models.alert import Alert
from tests.conftest import TestingSessionLocal


# ===========================================================================
# Health Check Tests
# ===========================================================================

def test_health_check(client):
    """Verify that the API health check route returns a successful status payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "StormShield API"}


# ===========================================================================
# User Profile API Tests
# ===========================================================================

def test_profiles_crud(client, db: Session):
    """Test full Profile CRUD API lifecycle (create, read, update, delete, error handling, duplicate prevention)."""
    # 1. Get profiles initially empty
    response = client.get("/api/profiles")
    assert response.status_code == 200
    assert response.json() == []

    # 2. Create a profile
    profile_data = {
        "name": "Aarav Sharma",
        "city": "Mumbai",
        "family_size": 4,
        "has_elderly": True,
        "has_children": False,
        "has_pets": True,
        "dwelling_type": "ground_floor",
        "health_conditions": "Asthma",
        "has_vehicle": True,
        "near_water_body": True,
        "preferred_language": "hi"
    }
    response = client.post("/api/profiles", json=profile_data)
    assert response.status_code == 201
    res_json = response.json()
    assert res_json["name"] == "Aarav Sharma"
    assert res_json["city"] == "Mumbai"
    assert "id" in res_json
    profile_id = res_json["id"]

    # 3. Prevent duplicate names
    response = client.post("/api/profiles", json=profile_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Profile name already exists"

    # 4. Fetch specific profile (success & failure)
    response = client.get(f"/api/profiles/{profile_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Aarav Sharma"

    response = client.get("/api/profiles/99999")
    assert response.status_code == 404

    # 5. Update profile
    update_data = {
        "preferred_language": "en",
        "has_vehicle": False
    }
    response = client.put(f"/api/profiles/{profile_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["preferred_language"] == "en"
    assert response.json()["has_vehicle"] is False

    response = client.put("/api/profiles/99999", json=update_data)
    assert response.status_code == 404

    # 6. Delete profile
    response = client.delete(f"/api/profiles/{profile_id}")
    assert response.status_code == 204

    response = client.delete("/api/profiles/99999")
    assert response.status_code == 404


# ===========================================================================
# Weather API Tests
# ===========================================================================

def test_weather_endpoints(client):
    """Test retrieving weather and setting/clearing weather overrides via endpoints."""
    # 1. Get weather
    response = client.get("/api/weather/Bengaluru")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["city"] == "Bengaluru"
    assert res_json["source"] == "simulated"

    # 2. Set scenario override
    override_data = {"scenario": "heavy_rain"}
    response = client.post("/api/weather/override", json=override_data)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "scenario": "heavy_rain"}

    # Fetch weather again to check override
    response = client.get("/api/weather/Mumbai")
    assert response.json()["source"] == "override"
    assert response.json()["condition"] == "Heavy Rain"

    # 3. Clear override
    response = client.delete("/api/weather/override")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "scenario": None}

    # Fetch weather again to verify override cleared
    response = client.get("/api/weather/Mumbai")
    assert response.json()["source"] == "simulated"


# ===========================================================================
# Plans API Tests
# ===========================================================================

mock_plan = {
    "phases": [
        {
            "phase": "before",
            "title": "Before Monsoon — Preparation",
            "items": [
                {
                    "category": "Home",
                    "description": "Clean drains",
                    "priority": "high",
                    "personalized_note": "Crucial for ground floors"
                }
            ]
        },
        {
            "phase": "during",
            "title": "During Monsoon — Active Safety",
            "items": []
        },
        {
            "phase": "after",
            "title": "After Monsoon — Recovery",
            "items": []
        }
    ],
    "current_phase": "before",
    "profile_summary": "Tailored plan for Aarav"
}


def test_plans_endpoints(client, db: Session):
    """Test the preparedness plans endpoints: profile checking, fresh generation, cache hits, and regeneration."""
    # 1. Profile not found
    response = client.get("/api/plans/99999")
    assert response.status_code == 404

    # 2. Create valid profile
    profile = UserProfile(name="Test Plan Profile", city="Mumbai", preferred_language="en")
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # 3. Get plan (fresh fetch, calls AI service, caches result)
    with patch("app.services.ai_service.generate_plan", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_plan

        response = client.get(f"/api/plans/{profile.id}")
        assert response.status_code == 200
        assert response.json()["profile_summary"] == "Tailored plan for Aarav"
        mock_gen.assert_called_once()

    # 4. Get plan again (cache hit, does NOT call AI service)
    with patch("app.services.ai_service.generate_plan", new_callable=AsyncMock) as mock_gen:
        response = client.get(f"/api/plans/{profile.id}")
        assert response.status_code == 200
        assert response.json()["profile_summary"] == "Tailored plan for Aarav"
        mock_gen.assert_not_called()

    # 5. Regenerate plan (invalidates cache, calls AI service, updates cache)
    with patch("app.services.ai_service.generate_plan", new_callable=AsyncMock) as mock_gen:
        updated_plan = mock_plan.copy()
        updated_plan["profile_summary"] = "Regenerated plan"
        mock_gen.return_value = updated_plan

        response = client.post(f"/api/plans/{profile.id}/regenerate")
        assert response.status_code == 200
        assert response.json()["profile_summary"] == "Regenerated plan"
        mock_gen.assert_called_once()

    # Check 404 for regenerate
    response = client.post("/api/plans/99999/regenerate")
    assert response.status_code == 404


# ===========================================================================
# Dashboard API Tests
# ===========================================================================

mock_dashboard = {
    "risk_score": {
        "score": 85,
        "level": "high",
        "explanation": "High rainfall region"
    },
    "checklist": {
        "items": [
            {
                "item": "Stock emergency water",
                "category": "Supplies",
                "is_personalized": True,
                "reason": "Family of 4"
            }
        ]
    },
    "travel": {
        "safety_rating": "caution",
        "summary": "Waterlogging on usual routes",
        "tips": ["Avoid subways"]
    },
    "safety": {
        "tips": [
            {
                "category": "electrical",
                "icon": "⚡",
                "tip": "Avoid touching poles"
            }
        ]
    }
}


def test_dashboard_endpoint(client, db: Session):
    """Test retrieving dashboard data: profile check, mock AI response validation, caching, and active alerts integration."""
    # 1. Profile not found
    response = client.get("/api/dashboard/99999")
    assert response.status_code == 404

    # 2. Setup profile and active alerts
    profile = UserProfile(name="Test Dash Profile", city="Chennai", preferred_language="en")
    db.add(profile)
    
    # Active alert for Chennai
    alert = Alert(
        severity="info",
        title="Heavy Winds",
        description="Wind speed up to 40 km/h",
        affected_area="Chennai",
        recommended_actions="[]",
        is_active=True
    )
    db.add(alert)
    db.commit()
    db.refresh(profile)

    # 3. Get dashboard
    with patch("app.services.ai_service.generate_dashboard", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_dashboard

        response = client.get(f"/api/dashboard/{profile.id}")
        assert response.status_code == 200
        res_json = response.json()
        assert res_json["risk_score"]["score"] == 85
        assert res_json["checklist"]["items"][0]["item"] == "Stock emergency water"
        assert len(res_json["recent_alerts"]) == 1
        assert res_json["recent_alerts"][0]["title"] == "Heavy Winds"
        mock_gen.assert_called_once()


# ===========================================================================
# Alerts API Tests
# ===========================================================================

def test_alerts_endpoints(client, db: Session):
    """Test endpoints for retrieving active weather alerts and controlling the Demo Mode alert timeline."""
    # 1. Get active alerts
    alert = Alert(
        severity="critical",
        title="Severe Flood",
        description="Evacuate ground floors",
        affected_area="Pune",
        recommended_actions="[]",
        is_active=True
    )
    db.add(alert)
    db.commit()

    response = client.get("/api/alerts?city=Pune")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Severe Flood"

    # 2. Demo timeline start
    with patch("app.services.alert_service.start_demo_timeline", new_callable=AsyncMock) as mock_start:
        response = client.post("/api/alerts/demo/start?city=Pune")
        assert response.status_code == 200
        assert response.json() == {"status": "demo_started", "city": "Pune"}
        mock_start.assert_called_once_with("Pune", TestingSessionLocal)

    # 3. Demo timeline stop
    with patch("app.services.alert_service.stop_demo_timeline", new_callable=AsyncMock) as mock_stop:
        response = client.post("/api/alerts/demo/stop")
        assert response.status_code == 200
        assert response.json() == {"status": "demo_stopped"}
        mock_stop.assert_called_once()


# ===========================================================================
# Chat API Tests
# ===========================================================================

def test_chat_endpoint(client, db: Session):
    """Test the POST /api/chat route: validating user message context, mock AI response formatting, and 404 profiles."""
    # 1. Profile not found
    chat_payload = {
        "profile_id": 99999,
        "message": "Is it safe to drive today?",
        "page_context": "dashboard",
        "history": []
    }
    response = client.post("/api/chat", json=chat_payload)
    assert response.status_code == 404

    # 2. Setup valid profile
    profile = UserProfile(name="Test Chat Profile", city="Mumbai", preferred_language="en")
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # 3. Execute chat
    chat_payload["profile_id"] = profile.id
    with patch("app.services.ai_service.chat_reply", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "Yes, but drive carefully. Wind speed is 25km/h."

        response = client.post("/api/chat", json=chat_payload)
        assert response.status_code == 200
        assert response.json() == {"reply": "Yes, but drive carefully. Wind speed is 25km/h."}
        mock_chat.assert_called_once()

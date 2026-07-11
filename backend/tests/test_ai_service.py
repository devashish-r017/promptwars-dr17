"""Unit tests for the AI service prompts and utilities."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage
from app.services import ai_service


def test_parse_json_clean():
    """Verify that a clean JSON string is successfully parsed into a dictionary."""
    clean_json = '{"key": "value", "list": [1, 2]}'
    parsed = ai_service._parse_json(clean_json)
    assert parsed == {"key": "value", "list": [1, 2]}


def test_parse_json_markdown():
    """Verify that JSON wrapped in markdown code blocks is successfully cleaned and parsed."""
    markdown_json = '```json\n{"key": "value"}\n```'
    parsed = ai_service._parse_json(markdown_json)
    assert parsed == {"key": "value"}


def test_parse_json_invalid():
    """Verify that invalid JSON returns an error dictionary instead of raising an exception."""
    invalid_json = '{"key": "value"'
    parsed = ai_service._parse_json(invalid_json)
    assert "error" in parsed
    assert parsed["error"] == "Failed to parse AI response"


@pytest.mark.asyncio
async def test_generate_plan_flow(mock_gemini):
    """Test generating a personalized preparedness plan through the mocked Gemini LLM."""
    # Mock return a valid plans JSON
    valid_plans_json = json.dumps({
        "phases": [{"phase": "before", "title": "Before", "items": []}],
        "current_phase": "before",
        "profile_summary": "Summary"
    })
    mock_gemini.mock_response = valid_plans_json

    profile = {"name": "Test User"}
    weather = {"monsoon_phase": "active_monsoon"}

    result = await ai_service.generate_plan(profile, weather, "en")
    assert result["current_phase"] == "before"
    assert len(result["phases"]) == 1


@pytest.mark.asyncio
async def test_generate_dashboard_flow(mock_gemini):
    """Test generating aggregated dashboard assessments via mock Gemini LLM."""
    # Mock return a valid dashboard JSON
    valid_dashboard_json = json.dumps({
        "risk_score": {"score": 42, "level": "moderate", "explanation": "Ok"},
        "checklist": {"items": []},
        "travel": {"safety_rating": "safe", "summary": "Ok", "tips": []},
        "safety": {"tips": []}
    })
    mock_gemini.mock_response = valid_dashboard_json

    profile = {"name": "Test User"}
    weather = {"severity": "normal"}

    result = await ai_service.generate_dashboard(profile, weather, "en")
    assert result["risk_score"]["score"] == 42


@pytest.mark.asyncio
async def test_chat_reply_flow(mock_gemini):
    """Test getting contextual chat response from the assistant via mock Gemini LLM."""
    mock_gemini.mock_response = "Hello there!"

    profile = {"name": "Test User"}
    weather = {"severity": "normal"}
    history = [{"role": "user", "content": "Hi"}]

    result = await ai_service.chat_reply(
        profile_dict=profile,
        weather_dict=weather,
        message="Hello",
        page_context="dashboard",
        history=history,
        language="en"
    )
    assert result == "Hello there!"

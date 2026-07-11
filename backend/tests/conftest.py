"""Pytest configuration and global fixtures for testing."""

import os
import sys
from typing import AsyncGenerator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Add backend root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# 2. Setup SQLite test database
TEST_DATABASE_URL = "sqlite:///./test_stormshield.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 3. Patch database variables before importing app/main modules
import app.database
app.database.SessionLocal = TestingSessionLocal
app.database.engine = test_engine

from app.database import Base, get_db
from app.main import app

# 4. Dependency override for FastAPI route handlers
def override_get_db():
    """Dependency override to yield a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clean_db():
    """Recreate tables before each test to guarantee complete isolation."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    """Session fixture for direct service testing."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """Sync HTTP client fixture for route integration testing."""
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def mock_gemini(monkeypatch):
    """Global mock for Google Gemini LLM using a custom BaseChatModel."""
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage
    from langchain_core.outputs import ChatResult, ChatGeneration

    class FakeGemini(BaseChatModel):
        mock_response: str = "{}"

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self.mock_response))])

        async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self.mock_response))])

        @property
        def _llm_type(self) -> str:
            return "fake-gemini"

    fake_llm = FakeGemini()
    
    # Patch the ChatGoogleGenerativeAI class used in ai_service
    monkeypatch.setattr("app.services.ai_service.ChatGoogleGenerativeAI", lambda *args, **kwargs: fake_llm)
    
    return fake_llm


@pytest.fixture(autouse=True)
def clear_weather_key(monkeypatch):
    """Ensure that the OpenWeatherMap API key is empty by default during tests so fallback paths execute."""
    monkeypatch.setenv("OPENWEATHERMAP_API_KEY", "")


@pytest.fixture(autouse=True)
def mock_weather_http(monkeypatch):
    """Globally mock httpx.AsyncClient.get to prevent any real network requests during tests."""
    from unittest.mock import MagicMock
    import httpx
    
    original_get = httpx.AsyncClient.get
    
    async def fake_get(self, url, params=None, **kwargs):
        url_str = str(url)
        if "geocoding-api.open-meteo.com" in url_str:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "results": [{
                    "name": "TestCity",
                    "latitude": 12.97,
                    "longitude": 77.59,
                    "country_code": "IN",
                    "country": "India"
                }]
            }
            return resp
        elif "api.open-meteo.com" in url_str:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "current": {
                    "temperature_2m": 28.0,
                    "relative_humidity_2m": 80.0,
                    "wind_speed_10m": 15.0,
                    "precipitation": 10.0,
                    "weather_code": 3
                }
            }
            return resp
        elif "api.openweathermap.org" in url_str:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "main": {"temp": 28.0, "humidity": 80},
                "wind": {"speed": 4.17},  # 15 km/h
                "weather": [{"main": "Clouds", "description": "overcast clouds"}],
                "rain": {"1h": 10.0}
            }
            return resp
        else:
            return await original_get(self, url, params=params, **kwargs)
        



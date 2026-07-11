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

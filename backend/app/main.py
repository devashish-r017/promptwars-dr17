"""StormShield backend — FastAPI application entry point."""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env before any imports that use os.getenv
load_dotenv()

from app.database import init_db
from app.api import profiles, weather, plans, dashboard, alerts, chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="StormShield API",
    description="AI-powered monsoon preparedness platform",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(profiles.router)
app.include_router(weather.router)
app.include_router(plans.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)
app.include_router(chat.router)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on first run."""
    # Import models so they are registered with Base
    import app.models  # noqa: F401
    init_db()
    logger.info("StormShield API started. Database initialized.")
    logger.info("Gemini model: %s", os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    logger.info("OpenWeatherMap: %s", "configured" if os.getenv("OPENWEATHERMAP_API_KEY") else "not configured (using simulated)")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "StormShield API"}

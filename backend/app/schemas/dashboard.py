"""Pydantic schemas for dashboard aggregate data."""

from pydantic import BaseModel
from app.schemas.weather import WeatherDataResponse
from app.schemas.alert import AlertResponse


class RiskScore(BaseModel):
    score: int  # 0-100
    level: str  # "low", "moderate", "high", "very_high"
    explanation: str  # Why this score


class ChecklistItem(BaseModel):
    item: str
    category: str
    is_personalized: bool = False
    reason: str | None = None  # Why this is added


class QuickChecklist(BaseModel):
    items: list[ChecklistItem]


class TravelStatus(BaseModel):
    safety_rating: str  # "safe", "caution", "avoid"
    summary: str
    tips: list[str]


class SafetyTip(BaseModel):
    category: str  # "electrical", "waterlogging", "health", "structural"
    icon: str  # emoji
    tip: str


class SafetyTips(BaseModel):
    tips: list[SafetyTip]


class DashboardResponse(BaseModel):
    weather: WeatherDataResponse
    risk_score: RiskScore
    checklist: QuickChecklist
    travel: TravelStatus
    safety: SafetyTips
    recent_alerts: list[AlertResponse]

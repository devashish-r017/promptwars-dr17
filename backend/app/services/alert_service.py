"""Alert service — CRUD + Demo Mode timeline."""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.schemas.alert import AlertResponse

logger = logging.getLogger(__name__)

# In-memory handle to cancel a running demo
_demo_task: asyncio.Task | None = None


def get_active_alerts(db: Session, city: str) -> list[AlertResponse]:
    """Return all active, non-expired alerts for a city."""
    now = datetime.now(timezone.utc)
    alerts = (
        db.query(Alert)
        .filter(
            Alert.affected_area == city,
            Alert.is_active == True,
        )
        .order_by(Alert.created_at.desc())
        .limit(20)
        .all()
    )

    results = []
    for a in alerts:
        # Check expiry
        if a.expires_at and a.expires_at.replace(tzinfo=timezone.utc) < now:
            a.is_active = False
            db.commit()
            continue
        results.append(AlertResponse(
            id=a.id,
            severity=a.severity,
            title=a.title,
            description=a.description,
            affected_area=a.affected_area,
            recommended_actions=json.loads(a.recommended_actions) if a.recommended_actions else [],
            is_active=a.is_active,
            created_at=a.created_at,
            expires_at=a.expires_at,
        ))

    return results


def create_alert(db: Session, severity: str, title: str, description: str,
                 affected_area: str, actions: list[str],
                 expires_minutes: int | None = None) -> Alert:
    """Create a new alert."""
    alert = Alert(
        severity=severity,
        title=title,
        description=description,
        affected_area=affected_area,
        recommended_actions=json.dumps(actions, ensure_ascii=False),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        expires_at=(datetime.now(timezone.utc) + timedelta(minutes=expires_minutes))
        if expires_minutes else None,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


# ---------------------------------------------------------------------------
# Demo Mode timeline — escalating alerts over ~2.5 minutes
# ---------------------------------------------------------------------------

_DEMO_TIMELINE = [
    {
        "delay_seconds": 0,
        "severity": "info",
        "title": "🌧️ Rain Watch Issued",
        "description": "Light to moderate rainfall expected over the next 6 hours. No immediate threat but stay updated.",
        "actions": [
            "Keep an umbrella and raincoat handy",
            "Check drainage around your home",
            "Charge your mobile devices",
        ],
        "expires_minutes": 10,
    },
    {
        "delay_seconds": 30,
        "severity": "warning",
        "title": "⚠️ Heavy Rain Warning",
        "description": "Heavy rainfall alert issued by IMD. Rainfall may exceed 100mm in the next 3 hours. Waterlogging expected in low-lying areas.",
        "actions": [
            "Avoid unnecessary travel",
            "Move valuables to higher shelves",
            "Stock up on drinking water and food",
            "Keep emergency kit accessible",
        ],
        "expires_minutes": 10,
    },
    {
        "delay_seconds": 60,
        "severity": "critical",
        "title": "🚨 Flood Alert — Low-Lying Areas",
        "description": "Flooding reported in low-lying areas. Water levels rising rapidly. Rivers and drains overflowing.",
        "actions": [
            "DO NOT walk or drive through floodwater",
            "Move to upper floors if water enters home",
            "Turn off electrical mains",
            "Call emergency services if trapped: 112",
            "Keep important documents in a waterproof bag",
        ],
        "expires_minutes": 10,
    },
    {
        "delay_seconds": 90,
        "severity": "critical",
        "title": "🆘 Evacuation Advisory",
        "description": "Residents in flood-prone zones are advised to evacuate to designated shelters. Emergency rescue teams deployed.",
        "actions": [
            "Evacuate to nearest shelter immediately",
            "Carry emergency kit, medicines, and ID documents",
            "Do not return home until authorities declare it safe",
            "Follow official communication channels only",
            "Help elderly and children first",
        ],
        "expires_minutes": 10,
    },
    {
        "delay_seconds": 150,
        "severity": "info",
        "title": "✅ Situation Stabilizing",
        "description": "Rainfall intensity decreasing. Flood waters receding in most areas. Remain cautious and avoid waterlogged streets.",
        "actions": [
            "Wait for official all-clear before returning home",
            "Check for structural damage before re-entering",
            "Boil drinking water as a precaution",
            "Report any downed power lines to authorities",
        ],
        "expires_minutes": 15,
    },
]


async def start_demo_timeline(city: str, db_factory) -> None:
    """Start the demo alert timeline. Spawns a background async task."""
    global _demo_task

    # Cancel any existing demo
    await stop_demo_timeline()

    async def _run_timeline():
        """Asynchronous worker that steps through the timeline stages and posts alerts."""
        for step in _DEMO_TIMELINE:
            await asyncio.sleep(step["delay_seconds"] if step != _DEMO_TIMELINE[0] else 0)
            # Create alert in a new DB session
            db = db_factory()
            try:
                create_alert(
                    db=db,
                    severity=step["severity"],
                    title=step["title"],
                    description=step["description"],
                    affected_area=city,
                    actions=step["actions"],
                    expires_minutes=step.get("expires_minutes"),
                )
                logger.info("Demo alert created: %s", step["title"])
            finally:
                db.close()

    _demo_task = asyncio.create_task(_run_timeline())


async def stop_demo_timeline() -> None:
    """Cancel a running demo timeline."""
    global _demo_task
    if _demo_task and not _demo_task.done():
        _demo_task.cancel()
        try:
            await _demo_task
        except asyncio.CancelledError:
            pass
    _demo_task = None

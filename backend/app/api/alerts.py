"""Alert routes — feed + Demo Mode controls."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.schemas.alert import AlertResponse
from app.services import alert_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
def get_alerts(city: str, db: Session = Depends(get_db)):
    return alert_service.get_active_alerts(db, city)


@router.post("/demo/start")
async def start_demo(city: str = "Mumbai"):
    await alert_service.start_demo_timeline(city, SessionLocal)
    return {"status": "demo_started", "city": city}


@router.post("/demo/stop")
async def stop_demo():
    await alert_service.stop_demo_timeline()
    return {"status": "demo_stopped"}

"""Cache service — SQLite-backed AI response cache with TTL."""

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.cached_response import CachedResponse


def get_cached(
    db: Session,
    profile_id: int,
    content_type: str,
    weather_hash: str,
    language: str,
) -> dict | None:
    """Return cached response if exists and not expired."""
    entry = (
        db.query(CachedResponse)
        .filter(
            CachedResponse.profile_id == profile_id,
            CachedResponse.content_type == content_type,
            CachedResponse.weather_scenario_hash == weather_hash,
            CachedResponse.language == language,
        )
        .first()
    )
    if entry is None:
        return None

    # Check TTL
    age = (datetime.now(timezone.utc) - entry.created_at.replace(tzinfo=timezone.utc)).total_seconds()
    if age > entry.ttl_seconds:
        db.delete(entry)
        db.commit()
        return None

    return json.loads(entry.response_json)


def set_cached(
    db: Session,
    profile_id: int,
    content_type: str,
    weather_hash: str,
    language: str,
    response_data: dict,
    ttl_seconds: int = 3600,
) -> None:
    """Store or update a cache entry."""
    # Delete existing entry for same key
    db.query(CachedResponse).filter(
        CachedResponse.profile_id == profile_id,
        CachedResponse.content_type == content_type,
        CachedResponse.weather_scenario_hash == weather_hash,
        CachedResponse.language == language,
    ).delete()

    entry = CachedResponse(
        profile_id=profile_id,
        content_type=content_type,
        weather_scenario_hash=weather_hash,
        language=language,
        response_json=json.dumps(response_data, ensure_ascii=False),
        ttl_seconds=ttl_seconds,
    )
    db.add(entry)
    db.commit()


def invalidate(db: Session, profile_id: int, content_type: str | None = None) -> int:
    """Clear cache for a profile. Returns number of deleted entries."""
    query = db.query(CachedResponse).filter(CachedResponse.profile_id == profile_id)
    if content_type:
        query = query.filter(CachedResponse.content_type == content_type)
    count = query.delete()
    db.commit()
    return count

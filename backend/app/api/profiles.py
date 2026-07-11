"""Profile CRUD routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_profile import UserProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.services import cache_service

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

PROFILE_NOT_FOUND = "Profile not found"


@router.get("", response_model=list[ProfileResponse])
def list_profiles(db: Session = Depends(get_db)):
    return db.query(UserProfile).order_by(UserProfile.updated_at.desc()).all()


@router.post("", response_model=ProfileResponse, status_code=201)
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    # Check for duplicate name
    existing = db.query(UserProfile).filter(UserProfile.name == data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Profile name already exists")

    profile = UserProfile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=PROFILE_NOT_FOUND)
    return profile


@router.put("/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: int, data: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=PROFILE_NOT_FOUND)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)

    # Invalidate cache when profile changes
    cache_service.invalidate(db, profile_id)

    return profile


@router.delete("/{profile_id}", status_code=204)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=PROFILE_NOT_FOUND)

    cache_service.invalidate(db, profile_id)
    db.delete(profile)
    db.commit()

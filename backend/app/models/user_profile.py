"""UserProfile model — stores family/dwelling context for AI personalization."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    family_size: Mapped[int] = mapped_column(Integer, default=1)
    has_elderly: Mapped[bool] = mapped_column(Boolean, default=False)
    has_children: Mapped[bool] = mapped_column(Boolean, default=False)
    has_pets: Mapped[bool] = mapped_column(Boolean, default=False)
    dwelling_type: Mapped[str] = mapped_column(String(30), default="independent_house")
    health_conditions: Mapped[str | None] = mapped_column(String(500), nullable=True)
    has_vehicle: Mapped[bool] = mapped_column(Boolean, default=False)
    near_water_body: Mapped[bool] = mapped_column(Boolean, default=False)
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """Convert profile ORM object to dict for AI prompt."""
        return {
            "name": self.name,
            "city": self.city,
            "family_size": self.family_size,
            "has_elderly": self.has_elderly,
            "has_children": self.has_children,
            "has_pets": self.has_pets,
            "dwelling_type": self.dwelling_type,
            "health_conditions": self.health_conditions,
            "has_vehicle": self.has_vehicle,
            "near_water_body": self.near_water_body,
        }


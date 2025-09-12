from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .types import GUID, JSONFlexible


class UserPreference(Base):
    """User preferences model storing locale, timezone, and custom JSON preferences."""
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    locale: Mapped[str | None] = mapped_column(String(20), default="vi-VN")
    timezone: Mapped[str | None] = mapped_column(String(64), default="Asia/Ho_Chi_Minh")
    interests: Mapped[list[str] | None] = mapped_column(JSONFlexible)
    habits: Mapped[list[str] | None] = mapped_column(JSONFlexible)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreference(id={self.id!r}, user_id={self.user_id!r})>"
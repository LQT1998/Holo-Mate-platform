import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from .base import Base, GUID


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    
    language = Column(String, default="en", nullable=False)
    timezone = Column(String, default="UTC", nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    notification_settings = Column(JSON) # e.g., {"new_message": true, "companion_update": false}
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="preferences")

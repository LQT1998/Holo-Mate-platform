import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base, GUID


class AICompanion(Base):
    __tablename__ = "ai_companions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    personality = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="active")
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="ai_companions")
    conversations = relationship("Conversation", back_populates="ai_companion", cascade="all, delete-orphan")
    character_asset = relationship("CharacterAsset", back_populates="ai_companion", uselist=False, cascade="all, delete-orphan")
    voice_profile = relationship("VoiceProfile", back_populates="ai_companion", uselist=False, cascade="all, delete-orphan")
    streaming_sessions = relationship("StreamingSession", back_populates="companion", cascade="all, delete-orphan")

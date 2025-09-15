import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base, GUID


class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    ai_companion_id = Column(GUID(), ForeignKey("ai_companions.id"), nullable=False, index=True)
    
    # ID from external TTS provider like ElevenLabs
    provider_voice_id = Column(String, nullable=False)
    provider_name = Column(String, default="elevenlabs", nullable=False)
    
    settings = Column(JSON) # e.g., {"stability": 0.5, "clarity": 0.75}
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    ai_companion = relationship("AICompanion", back_populates="voice_profile")

import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class CharacterAsset(Base):
    __tablename__ = "character_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_companion_id = Column(UUID(as_uuid=True), ForeignKey("ai_companions.id"), nullable=False, index=True)
    model_url = Column(String, nullable=False)
    asset_type = Column(String, default="3d_model", nullable=False)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    ai_companion = relationship("AICompanion", back_populates="character_asset")
    animations = relationship("AnimationSequence", back_populates="character_asset", cascade="all, delete-orphan")

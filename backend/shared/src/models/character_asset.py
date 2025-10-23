import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base, GUID


class CharacterAsset(Base):
    __tablename__ = "character_assets"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    ai_companion_id = Column(GUID(), ForeignKey("ai_companions.id"), nullable=False, index=True)
    character_id = Column(String, nullable=False)
    model_url = Column(String, nullable=True)
    asset_type = Column(String, default="3d_model", nullable=False)
    animations_data = Column(JSON, nullable=True)
    emotions_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    ai_companion = relationship("AICompanion", back_populates="character_asset")
    animations = relationship("AnimationSequence", back_populates="character_asset", cascade="all, delete-orphan")

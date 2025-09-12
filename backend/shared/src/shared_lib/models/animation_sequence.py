import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class AnimationSequence(Base):
    __tablename__ = "animation_sequences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_asset_id = Column(UUID(as_uuid=True), ForeignKey("character_assets.id"), nullable=False, index=True)
    
    trigger_event = Column(String, nullable=False, index=True) # e.g., "on_greeting", "on_laugh"
    animation_url = Column(String, nullable=False)
    metadata = Column(JSON) # e.g., {"duration": 2.5, "loop": false}
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    character_asset = relationship("CharacterAsset", back_populates="animations")

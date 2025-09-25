import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base, GUID


class Message(Base):
    __tablename__ = "messages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(GUID(), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" or "companion"
    content = Column(Text, nullable=False)
    content_type = Column(String, default="text", nullable=False) # "text", "audio_url"
    
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

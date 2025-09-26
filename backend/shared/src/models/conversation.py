import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped

from .base import Base, GUID

if TYPE_CHECKING:
    from .user import User
    from .ai_companion import AICompanion
    from .message import Message
    from .streaming_session import StreamingSession


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ai_companion_id = Column(GUID(), ForeignKey("ai_companions.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    ai_companion: Mapped["AICompanion"] = relationship("AICompanion", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    streaming_sessions: Mapped[list["StreamingSession"]] = relationship("StreamingSession", back_populates="conversation", cascade="all, delete-orphan")

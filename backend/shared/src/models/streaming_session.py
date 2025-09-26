"""
StreamingSession model for managing device streaming sessions
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Enum, Index, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base, GUID


class SessionStatus(PyEnum):
    """Streaming session status enum"""
    ACTIVE = "active"
    CONNECTING = "connecting"
    ERROR = "error"
    EXPIRED = "expired"
    ENDED = "ended"


class StreamingSession(Base):
    """Model for streaming sessions between devices and server"""
    
    __tablename__ = "streaming_sessions"
    
    id = Column(GUID(), primary_key=True, default=uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    device_id = Column(GUID(), ForeignKey("hologram_devices.id"), nullable=False)
    conversation_id = Column(GUID(), ForeignKey("conversations.id"), nullable=True)
    companion_id = Column(GUID(), ForeignKey("ai_companions.id"), nullable=True)
    
    # Session status
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.ACTIVE)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    last_active_at = Column(DateTime, nullable=True, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    
    # Configuration
    streaming_config = Column(JSON, nullable=True)
    audio_settings = Column(JSON, nullable=True)
    
    # Additional metadata
    session_metadata = Column(JSON, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_streaming_sessions_user_id', 'user_id'),
        Index('ix_streaming_sessions_device_id', 'device_id'),
        Index('ix_streaming_sessions_status', 'status'),
        Index('ix_streaming_sessions_expires_at', 'expires_at'),
        Index('ix_streaming_sessions_user_status', 'user_id', 'status'),
        Index('ix_streaming_sessions_device_status', 'device_id', 'status'),
    )
    
    # Relationships
    user = relationship("User", back_populates="streaming_sessions")
    device = relationship("HologramDevice", back_populates="streaming_sessions")
    conversation = relationship("Conversation", back_populates="streaming_sessions")
    companion = relationship("AICompanion", back_populates="streaming_sessions")
    
    def __repr__(self) -> str:
        return f"<StreamingSession(id={self.id}, user_id={self.user_id}, device_id={self.device_id}, status={self.status})>"

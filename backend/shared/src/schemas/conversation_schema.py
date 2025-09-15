"""
Pydantic schemas for Conversation entity
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class ConversationBase(BaseModel):
    """Base conversation schema with common fields"""
    title: Optional[str] = Field(None, max_length=200)
    ai_companion_id: uuid.UUID


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""
    pass


class ConversationUpdate(BaseModel):
    """Schema for updating conversation information"""
    title: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, pattern="^(active|paused|archived)$")


class ConversationResponse(ConversationBase):
    """Schema for conversation response"""
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

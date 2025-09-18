"""
Pydantic schemas for Message entity
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
import uuid


class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    content: str = Field(..., min_length=1, max_length=10000)
    role: str = Field(..., pattern="^(user|companion)$")
    content_type: str = Field(default="text", pattern="^(text|audio_url)$")
    conversation_id: str = Field(..., description="ID of the conversation this message belongs to")


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    content_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    """Schema for message list response with pagination"""
    messages: List[MessageResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
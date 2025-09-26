"""
Pydantic schemas for Message entity
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict
import uuid


class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    content: str = Field(..., min_length=1, max_length=10000)
    role: Literal["user", "companion"]
    content_type: Literal["text", "audio_url"] = "text"


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: Literal["user", "companion"]
    content: str
    content_type: Literal["text", "audio_url"]
    created_at: datetime
    updated_at: Optional[datetime] = Field(
        None, description="Timestamp of last update, null if never updated"
    )

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    """Schema for message list response with pagination"""
    messages: List[MessageResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
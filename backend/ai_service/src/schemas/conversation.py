"""
Conversation schemas for AI service
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
import uuid


class ConversationSettings(BaseModel):
    """Conversation settings schema"""
    voice_enabled: Optional[bool] = True
    emotion_detection: Optional[bool] = True
    response_length: Optional[Literal["short", "medium", "long"]] = "medium"
    formality_level: Optional[Literal["casual", "neutral", "formal"]] = "neutral"


class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    companion_id: Optional[uuid.UUID] = Field(
        None, description="AI Companion identifier"
    )
    status: Optional[
        Literal["active", "paused", "ended", "archived", "deleted"]
    ] = Field("active")  # hợp nhất tất cả state
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional conversation metadata"
    )
    settings: Optional[ConversationSettings] = None


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""
    companion_id: uuid.UUID = Field(..., description="AI Companion identifier")
    initial_message: Optional[str] = Field(None, max_length=5000)


class ConversationRead(ConversationBase):
    """Schema for reading conversation data"""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    message_count: int = 0
    initial_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationUpdate(BaseModel):
    """Schema for updating conversation data"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[
        Literal["active", "paused", "ended", "archived", "deleted"]
    ] = None
    metadata: Optional[Dict[str, Any]] = None
    settings: Optional[ConversationSettings] = None

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class ConversationListResponse(BaseModel):
    """Response schema for conversations list endpoint"""
    conversations: List[ConversationRead]
    total: int
    page: int
    per_page: int
    total_pages: int
    metadata: Optional[Dict[str, Any]] = None

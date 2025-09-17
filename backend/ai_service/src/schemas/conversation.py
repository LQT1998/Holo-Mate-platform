"""
Conversation schemas for AI service
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
import uuid


class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    companion_id: Optional[str] = Field(None, description="AI Companion identifier")
    status: Optional[Literal["active", "archived", "deleted"]] = Field("active")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional conversation metadata")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""
    pass


class ConversationRead(ConversationBase):
    """Schema for reading conversation data"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    message_count: int = 0

    class Config:
        from_attributes = True


class ConversationUpdate(BaseModel):
    """Schema for updating conversation data"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[Literal["active", "archived", "deleted"]] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"


class ConversationListResponse(BaseModel):
    """Response schema for conversations list endpoint"""
    conversations: List[ConversationRead]
    total: int
    page: int
    per_page: int
    total_pages: int
    metadata: Optional[Dict[str, Any]] = None

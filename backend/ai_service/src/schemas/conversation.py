"""
Conversation schemas for AI service
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List, Dict, Any, Literal, Union
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
    companion_id: Optional[uuid.UUID] = Field(None, description="AI Companion identifier")
    ai_companion_id: Optional[Union[uuid.UUID, str]] = Field(None, description="AI Companion identifier (alias for companion_id)")
    initial_message: Optional[str] = Field(None, max_length=5000)
    
    @field_validator('ai_companion_id', mode='before')
    @classmethod
    def validate_ai_companion_id(cls, v):
        """Convert string ai_companion_id to UUID if needed"""
        if isinstance(v, str):
            try:
                return uuid.UUID(v)
            except ValueError:
                # If it's not a valid UUID, create a stable one
                return uuid.uuid5(uuid.NAMESPACE_URL, f"dev:ai-companion:{v}")
        return v
    
    def model_post_init(self, __context) -> None:
        """Normalize ai_companion_id to companion_id"""
        if self.ai_companion_id and not self.companion_id:
            self.companion_id = self.ai_companion_id

    @model_validator(mode="after")
    def ensure_not_empty(self) -> "ConversationCreate":
        """In DEV, reject completely empty payload to satisfy contract tests."""
        if (
            self.title is None
            and self.companion_id is None
            and getattr(self, "ai_companion_id", None) is None
            and self.initial_message is None
            and self.metadata is None
            and self.settings is None
        ):
            # Raise Pydantic validation error by field
            raise ValueError("At least one field must be provided")
        return self


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

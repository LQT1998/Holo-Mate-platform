"""
Pydantic schemas for AI Companion data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid


class Personality(BaseModel):
    traits: Optional[List[str]] = None
    communication_style: Optional[str] = Field(default=None, min_length=1, max_length=50)
    humor_level: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    empathy_level: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class VoiceProfile(BaseModel):
    voice_id: Optional[str] = Field(default=None, min_length=1)
    speed: Optional[float] = Field(default=None, ge=0.1, le=3.0)
    pitch: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    volume: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class CharacterAsset(BaseModel):
    model_id: Optional[str] = Field(default=None, min_length=1)
    animations: Optional[List[str]] = None
    emotions: Optional[List[Literal["happy", "sad", "excited", "calm", "angry", "neutral"]]] = None
    # Avoid pydantic protected namespace warning for field name 'model_id'
    model_config = {
        "protected_namespaces": ()
    }


class Preferences(BaseModel):
    conversation_topics: Optional[List[str]] = None
    response_length: Optional[Literal["short", "medium", "long"]] = None
    formality_level: Optional[Literal["casual", "formal", "neutral"]] = None


class AICompanionBase(BaseModel):
    """Base AI Companion schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    personality: Optional[Personality] = None
    voice_profile: Optional[VoiceProfile] = None
    character_asset: Optional[CharacterAsset] = None
    preferences: Optional[Preferences] = None
    status: Literal["active", "inactive", "training", "error"]


class AICompanionRead(AICompanionBase):
    """Schema for reading AI Companion data"""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AICompanionListResponse(BaseModel):
    """Schema for AI Companions list response with pagination"""
    companions: List[AICompanionRead]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., gt=0)
    total_pages: int = Field(..., ge=0)


class AICompanionCreate(AICompanionBase):
    """Schema for creating a new AI Companion"""
    status: Optional[Literal["active", "inactive", "training", "error"]] = "active"


class AICompanionUpdate(BaseModel):
    """Schema for updating AI Companion"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    personality: Optional[Personality] = None
    voice_profile: Optional[VoiceProfile] = None
    character_asset: Optional[CharacterAsset] = None
    preferences: Optional[Preferences] = None
    status: Optional[Literal["active", "inactive", "training", "error"]] = None

    class Config:
        extra = "forbid"


class DeleteResponse(BaseModel):
    """Response model for DELETE /ai-companions/{id} endpoint"""
    message: str
    deleted_id: str

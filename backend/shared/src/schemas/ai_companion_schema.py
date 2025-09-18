"""
Pydantic schemas for AICompanion entity
"""

import uuid
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class Personality(BaseModel):
    traits: List[str]
    communication_style: Optional[str] = None
    humor_level: Optional[float] = None
    empathy_level: Optional[float] = None


class Preferences(BaseModel):
    conversation_topics: Optional[List[str]] = None
    response_length: Optional[Literal["short", "medium", "long"]] = None
    formality_level: Optional[Literal["casual", "neutral", "formal"]] = None


class VoiceProfile(BaseModel):
    voice_id: str
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0


class CharacterAsset(BaseModel):
    model_id: str
    animations: List[str]
    emotions: List[str]


class AICompanionBase(BaseModel):
    """Base AI companion schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    personality: Optional[Personality] = None
    preferences: Optional[Preferences] = None
    voice_profile: Optional[VoiceProfile] = None
    character_asset: Optional[CharacterAsset] = None
    status: Optional[Literal["active", "inactive", "training", "error"]] = "active"


class AICompanionCreate(AICompanionBase):
    """Schema for creating a new AI companion"""
    pass


class AICompanionUpdate(BaseModel):
    """Schema for updating AI companion information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    personality: Optional[Personality] = None
    preferences: Optional[Preferences] = None
    voice_profile: Optional[VoiceProfile] = None
    character_asset: Optional[CharacterAsset] = None
    status: Optional[Literal["active", "inactive", "training", "error"]] = None

    class Config:
        extra = "forbid"


class AICompanionResponse(AICompanionBase):
    """Schema for AI companion response"""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

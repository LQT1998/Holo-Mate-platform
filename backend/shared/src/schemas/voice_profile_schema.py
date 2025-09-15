"""
Pydantic schemas for VoiceProfile entity
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class VoiceProfileCreate(BaseModel):
    """Schema for creating a new voice profile"""
    provider_voice_id: str = Field(..., min_length=1, max_length=100)
    provider_name: str = Field(..., min_length=1, max_length=50)
    settings: Optional[Dict[str, Any]] = None


class VoiceProfileUpdate(BaseModel):
    """Schema for updating voice profile information"""
    provider_voice_id: Optional[str] = Field(None, min_length=1, max_length=100)
    provider_name: Optional[str] = Field(None, min_length=1, max_length=50)
    settings: Optional[Dict[str, Any]] = None


class VoiceProfileResponse(BaseModel):
    """Schema for voice profile response"""
    id: uuid.UUID
    ai_companion_id: uuid.UUID
    provider_voice_id: str
    provider_name: str
    settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

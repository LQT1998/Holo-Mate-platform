"""Pydantic schemas for VoiceProfile entity"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid


class VoiceProfileBase(BaseModel):
    """Base schema for voice profile data"""

    id: uuid.UUID = Field(..., description="Voice profile identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Display name")
    language: str = Field(..., min_length=2, max_length=10, description="Language code, e.g. en-US")
    gender: str = Field(..., min_length=1, max_length=20, description="Voice gender descriptor")
    sample_url: str = Field(..., description="URL to audio sample")
    created_at: datetime
    updated_at: datetime


class VoiceProfileResponse(VoiceProfileBase):
    """Schema for a single voice profile response"""


class VoiceProfileListResponse(BaseModel):
    """Schema for list voice profile response"""

    voice_profiles: List[VoiceProfileResponse]


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

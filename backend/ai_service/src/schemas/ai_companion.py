"""
Pydantic schemas for AI Companion data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
import uuid


class AICompanionBase(BaseModel):
    """Base AI Companion schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    personality: str = Field(..., min_length=1, max_length=1000)
    voice_profile: Optional[Dict[str, Any]] = None
    character_asset: Optional[Dict[str, Any]] = None
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
    """Schema for creating a new AI Companion.
    
    Same fields as base schema; used for POST requests.
    """
    pass


class AICompanionUpdate(BaseModel):
    """Schema for updating AI Companion"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    personality: Optional[str] = Field(None, min_length=1, max_length=1000)
    voice_profile: Optional[Dict[str, Any]] = None
    character_asset: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|training|error)$")

    class Config:
        extra = "forbid"

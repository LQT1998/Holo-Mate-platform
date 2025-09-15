"""
Pydantic schemas for AICompanion entity
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class AICompanionBase(BaseModel):
    """Base AI companion schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    personality: Optional[Dict[str, Any]] = None


class AICompanionCreate(AICompanionBase):
    """Schema for creating a new AI companion"""
    pass


class AICompanionUpdate(BaseModel):
    """Schema for updating AI companion information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    personality: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|archived)$")


class AICompanionResponse(AICompanionBase):
    """Schema for AI companion response"""
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

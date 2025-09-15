"""
Pydantic schemas for User entity
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
import uuid


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences"""
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    notifications_enabled: Optional[bool] = None
    notification_settings: Optional[Dict[str, Any]] = None


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response"""
    language: Optional[str] = None
    timezone: Optional[str] = None
    notifications_enabled: bool = True
    notification_settings: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPublic(UserResponse):
    """Schema for public user information"""
    pass


class UserProfileResponse(UserResponse):
    """Schema for detailed user profile response"""
    preferences: Optional[UserPreferencesResponse] = None

    class Config:
        from_attributes = True

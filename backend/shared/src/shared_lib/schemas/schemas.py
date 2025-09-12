from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl, constr

# ===================================================================
# Base Schemas
# ===================================================================


class UserBase(BaseModel):
    """Base schema for user properties."""
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str
    provider: Optional[str] = None
    provider_id: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    password: Optional[str] = None


# ===================================================================
# Public Schemas (for API responses)
# ===================================================================


class UserPublic(UserBase):
    """Schema for user information safe to be exposed to clients."""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token_expires_in: int


# ===================================================================
# Internal Schemas (for API requests)
# ===================================================================


class GoogleLoginRequest(BaseModel):
    """Request body for /auth/google."""
    id_token: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    """Request schema for email/username + password login."""
    email_or_username: str
    password: str


# ===================================================================
# Profile & Preferences Schemas
# ===================================================================


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


LocaleStr = constr(min_length=2, max_length=20)
TimezoneStr = constr(min_length=2, max_length=64)


class UserPreferencesUpdate(BaseModel):
    locale: Optional[LocaleStr] = None
    timezone: Optional[TimezoneStr] = None
    interests: Optional[List[str]] = None
    habits: Optional[List[str]] = None


class UserPreferencesResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    locale: Optional[LocaleStr] = None
    timezone: Optional[TimezoneStr] = None
    interests: Optional[List[str]] = None
    habits: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    # Add other profile fields here

class UserPreferencesUpdate(BaseModel):
    language: Optional[str] = None
    timezone: Optional[str] = None
    # Add other preference fields here

class UserPreferencesResponse(BaseModel):
    language: str
    timezone: str
    class Config:
        orm_mode = True

class UserPublic(UserBase):
    id: uuid.UUID
    is_active: bool
    class Config:
        orm_mode = True

class UserProfileResponse(UserPublic):
    # Inherits fields from UserPublic
    # Add any additional profile-specific fields here
    pass

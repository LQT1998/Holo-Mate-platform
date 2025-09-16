# backend/shared/src/schemas/user.py

from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: Union[str, int]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # để Pydantic đọc trực tiếp từ SQLAlchemy model


class UserUpdate(BaseModel):
    """Allowed fields for updating a user profile.

    Only first_name and last_name are permitted. Other fields are forbidden.
    """

    first_name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=2, max_length=50)

    class Config:
        extra = "forbid"

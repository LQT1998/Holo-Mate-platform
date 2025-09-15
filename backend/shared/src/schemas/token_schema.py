"""
Pydantic schemas for authentication tokens
"""

from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Lifetime of the access token in seconds
    refresh_token_expires_in: int  # Lifetime of the refresh token in seconds


class TokenData(BaseModel):
    """Schema for token data"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    scopes: list[str] = []

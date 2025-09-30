"""
Authentication service
"""
from __future__ import annotations

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_token_pair(self, user) -> tuple[str, str]:
        """Create access and refresh token pair for user (dict or model)."""
        from shared.src.security.jwt import create_access_token
        from datetime import timedelta

        # Support both dict-like and model objects
        email = None
        if isinstance(user, dict):
            email = user.get("email")
        else:
            email = getattr(user, "email", None)
        if not email:
            email = "unknown"

        access_token = create_access_token(
            data={"sub": str(email)},
            expires_delta=timedelta(minutes=30)
        )
        refresh_token = create_access_token(
            data={"sub": str(email), "type": "refresh"},
            expires_delta=timedelta(days=7)
        )
        return access_token, refresh_token
    
    async def rotate_refresh_token(self, refresh_token: str) -> tuple[object, str, str]:
        """Rotate refresh token to create new token pair."""
        # Placeholder implementation
        raise ValueError("Invalid refresh token")

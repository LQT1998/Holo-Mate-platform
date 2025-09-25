"""JWT utilities for encoding and verifying access tokens."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt

from shared.src.config import settings
from shared.src.constants import DEV_OWNER_ID


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token.

    Args:
        data: Payload to include in the token.
        expires_delta: Optional expiration delta. Defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: Encoded JWT token.
    """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


class JWTErrorResponse(HTTPException):
    """Custom HTTPException for JWT validation errors."""


def verify_access_token(token: str) -> dict[str, Any]:
    """Verify a JWT access token and return its payload.

    Args:
        token: JWT token to verify.

    Returns:
        dict[str, Any]: Decoded payload if valid.

    Raises:
        HTTPException: If token is invalid or expired.
    """

    # Allow DEV shortcut
    if getattr(settings, "ENV", "").lower() == "dev" and token == "valid_access_token_here":
        return {
            "id": str(DEV_OWNER_ID),
            "email": "test@example.com",
            "is_active": True,
            "sub": "test@example.com",
        }

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if "sub" not in payload:
            raise credentials_exception
        return payload
    except JWTError as error:
        raise JWTErrorResponse(
            status_code=credentials_exception.status_code,
            detail=credentials_exception.detail,
            headers=credentials_exception.headers,
        ) from error


"""
Dependency injection for authentication in AI service
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone

from ai_service.src.config import settings
from shared.src.security.security import verify_access_token  # dùng chung từ shared

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> dict:
    """
    Get current authenticated user from JWT token.
    In dev mode: allow fixed test token.
    In production: verify JWT using shared security utils.
    """
    try:
        token = credentials.credentials

        # Dev shortcut for contract tests
        if settings.DEV_MODE:
            if token == "valid_access_token_here":
                now = datetime.now(timezone.utc).isoformat()
                return {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "email": "test@example.com",
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                }
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials (dev mode)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # --- Production path ---
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "id": payload.get("user_id") or payload.get("sub"),
            "email": payload.get("email"),
            "is_active": True,  # JWT không lưu cờ này → giả định True
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

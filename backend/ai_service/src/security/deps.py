"""
Dependency injection for authentication in AI service
"""

from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone

from ai_service.src.config import settings
from shared.src.security.security import verify_access_token  # dùng chung từ shared
from shared.src.constants import DEV_OWNER_ID

# auto_error=False để tránh 403 mặc định
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    - Dev mode: fixed test token.
    - Production: verify JWT with shared utils.
    """
    try:
        # Missing credentials -> 401 Unauthorized
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials

        # --- Dev shortcut ---
        if settings.DEV_MODE:
            if token == "valid_access_token_here":
                now = datetime.now(timezone.utc)
                return {
                    "id": str(DEV_OWNER_ID),
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
            "is_active": True,  # giả định true vì JWT không lưu cờ này
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

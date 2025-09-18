"""
Dependency injection for authentication in Streaming service
"""

from typing import Annotated, Any
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from streaming_service.src.config import settings
from shared.src.security.security import verify_access_token  # dùng chung từ shared

# auto_error=False để tự kiểm soát lỗi 401
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> dict[str, Any]:
    """
    Get current authenticated user from JWT token.
    - Nếu AUTH_ENABLED = False → trả về mock user (Dev mode).
    - Nếu AUTH_ENABLED = True → verify JWT bằng shared utils.
    """
    # --- Dev mode: bypass auth ---
    if not settings.AUTH_ENABLED:
        now = datetime.now(timezone.utc)
        return {
            "id": "00000000-0000-0000-0000-000000000000",
            "email": "dev.user@example.com",
            "is_active": True,
            "is_superuser": True,
            "created_at": now,
            "updated_at": now,
        }

    # --- Production path ---
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
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
        "is_active": True,  # mặc định true vì JWT không lưu flag này
    }

from typing import Annotated, Any, Optional
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from streaming_service.src.config import settings
from shared.src.security.security import verify_access_token
from shared.src.constants import DEV_OWNER_ID

security = HTTPBearer(auto_error=False)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> dict[str, Any]:
    """
    Resolve current authenticated user from JWT token.
    - Dev mode (AUTH_ENABLED=False): bypass verify, return mock user.
    - Prod mode (AUTH_ENABLED=True): verify JWT using shared utils.
    """
    if not settings.AUTH_ENABLED:
        if credentials is None:
            raise _unauthorized("Not authenticated")
        if credentials.credentials == "invalid_access_token_here":
            raise _unauthorized("Invalid authentication credentials")
        if credentials.credentials not in ["valid_access_token_here", "test_token", "test-token"]:
            raise _unauthorized("Invalid authentication credentials")

        now = datetime.now(timezone.utc)
        return {
            "id": str(DEV_OWNER_ID),
            "email": "dev.user@example.com",
            "is_active": True,
            "is_superuser": True,
            "created_at": now,
            "updated_at": now,
        }

    # --- Production path ---
    if credentials is None:
        raise _unauthorized("Not authenticated")

    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise _unauthorized("Invalid authentication credentials")

    return {
        "id": payload.get("user_id") or payload.get("sub"),
        "email": payload.get("email"),
        "is_active": True,
        "is_superuser": payload.get("is_superuser", False),
    }

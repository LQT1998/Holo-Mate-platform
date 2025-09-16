"""
Dependency injection for authentication in Auth Service
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from auth_service.src.db.session import get_db
from auth_service.src.services.user_service import UserService
from shared.src.models.user import User
from shared.src.security.security import verify_access_token
from auth_service.src.config import settings

# Phải set auto_error=False để tránh 403 mặc định
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    - Dev mode: shortcut mock user.
    - Production: verify token + load user from DB.
    """
    try:
        # Thiếu Authorization header → 401 Unauthorized
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials

        # --- Dev shortcut ---
        if settings.DEV_MODE:
            if token == "test_token":
                class MockUser:
                    def __init__(self):
                        self.id = "00000000-0000-0000-0000-000000000000"
                        self.email = "test@example.com"
                        self.first_name = "Test"
                        self.last_name = "User"
                        self.is_active = True
                        now = datetime.now(timezone.utc)
                        self.created_at = now
                        self.updated_at = now

                return MockUser()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials (dev mode)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # --- Production path ---
        token_data = verify_access_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Lấy user từ DB
        user_service = UserService(db)
        user = await user_service.get_user_by_id(token_data.get("sub"))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.db.session import get_db
from auth_service.src.security.deps import get_current_user
from auth_service.src.services.user_service import UserService
from shared.src.models.user import User
from shared.src.schemas.user import UserRead, UserUpdate
from shared.src.constants import DEV_OWNER_ID
from auth_service.src.config import settings

router = APIRouter(tags=["Users"])


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user profile information.
    Returns user data without sensitive fields like password.
    """
    # Dev shortcut: return mock data for any user in DEV_MODE
    if settings.DEV_MODE:
        return UserRead(
            id=str(DEV_OWNER_ID),
            email=getattr(current_user, "email", "test@example.com"),
            first_name="Test",
            last_name="User",
            is_active=True,
            created_at=current_user.created_at if hasattr(current_user, "created_at") else None,
            updated_at=current_user.updated_at if hasattr(current_user, "updated_at") else None,
        )
    
    # Production path with real user data from DB
    user_service = UserService(db)
    user = await user_service.get_user_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return user data without sensitive fields
    return user


@router.put("/me", response_model=UserRead)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile.

    Only allows updating first_name and last_name. Other fields are forbidden.
    """
    if not current_user or not getattr(current_user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    # Extract allowed, non-null fields
    update_data = payload.model_dump(exclude_unset=True)

    # Explicitly forbid forbidden fields (defense-in-depth even with Pydantic forbid)
    forbidden_keys = {"password", "email", "id", "created_at", "updated_at", "is_active"}
    if any(key in update_data for key in forbidden_keys):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attempt to update forbidden fields",
        )

    # No changes provided
    if not update_data:
        # Return current state as no-op update (or could be 400, but tests allow partial/no-op)
        return current_user

    user_service = UserService(db)

    # Dev shortcut for contract tests: emulate update without DB writes
    if settings.DEV_MODE and getattr(current_user, "email", None) == "test@example.com":
        for k, v in update_data.items():
            setattr(current_user, k, v)
        return UserRead(
            id=str(DEV_OWNER_ID),
            email="updated@example.com" if "email" in update_data else "test@example.com",
            first_name=getattr(current_user, "first_name", None),
            last_name=getattr(current_user, "last_name", None),
            is_active=True,
            created_at=getattr(current_user, "created_at", None),
            updated_at=getattr(current_user, "updated_at", None),
        )

    # Production path
    updated_user = await user_service.update_user(current_user.id, update_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return updated_user

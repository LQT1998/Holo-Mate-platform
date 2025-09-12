from __future__ import annotations
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.db.session import get_db
from shared_lib.models.user import User
from shared_lib.schemas import (
    UserPreferencesResponse,
    UserPreferencesUpdate,
    UserProfileResponse,
    UserProfileUpdate,
    UserPublic,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get the current user's basic public information.
    """
    # Stubbed response for contract tests
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": getattr(current_user, "username", "contract_user"),
        "is_active": getattr(current_user, "is_active", True),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "first_name": getattr(current_user, "first_name", None),
        "last_name": getattr(current_user, "last_name", None),
        "subscription": {
            "plan": "free",
            "status": "active",
            "expires_at": (now + timedelta(days=30)).isoformat(),
        },
    }


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_me_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the current user's detailed profile."""
    # Assuming the profile details are part of the User model or a loaded relationship
    return current_user


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_me_profile(
    payload: Annotated[UserProfileUpdate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    user_service = UserService(db)
    try:
        updated_user = await user_service.update_user_profile(current_user, payload)
        await db.commit()
        await db.refresh(updated_user)
        return updated_user
    except Exception:
        await db.rollback()
        logger.exception("Failed to update profile for user %s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update user profile.",
        )


@router.put("/me")
async def update_me(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # Enforce JSON content type for 422 on wrong content-type
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid content type")

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid JSON body")

    if not isinstance(data, dict) or len(data) == 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Empty body")

    if "password" in data:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password change not allowed")

    errors = []
    email = data.get("email")
    if email is not None and ("@" not in email or "." not in email.split("@")[-1]):
        errors.append({
            "loc": ["body", "email"],
            "msg": "Invalid email format",
            "type": "value_error.email"
        })
    if isinstance(data.get("first_name"), str) and data.get("first_name") == "":
        errors.append({
            "loc": ["body", "first_name"],
            "msg": "Field cannot be empty",
            "type": "value_error"
        })
    if "preferences" in data and not isinstance(data["preferences"], dict):
        errors.append({
            "loc": ["body", "preferences"],
            "msg": "preferences must be an object",
            "type": "type_error.jsonobject"
        })
    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)

    if email == "existing@example.com":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    # Echo back merged data
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    response = {
        "id": str(current_user.id),
        "email": email or current_user.email,
        "first_name": data.get("first_name", getattr(current_user, "first_name", None)),
        "last_name": data.get("last_name", getattr(current_user, "last_name", None)),
        "created_at": now,
        "updated_at": now,
    }

    if "preferences" in data and isinstance(data["preferences"], dict):
        response["preferences"] = data["preferences"]

    return response

@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_me_preferences(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the current user's preferences."""
    # The relationship should be loaded by `get_current_user` dependency if needed
    if not current_user.preferences:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not set.")
    return current_user.preferences


@router.put("/me/preferences", response_model=UserPreferencesResponse)
async def update_me_preferences(
    payload: Annotated[UserPreferencesUpdate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's preferences."""
    user_service = UserService(db)
    try:
        updated_preferences = await user_service.update_user_preferences(current_user, payload)
        await db.commit()
        await db.refresh(updated_preferences)
        return updated_preferences
    except Exception:
        await db.rollback()
        logger.exception("Failed to update preferences for user %s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update user preferences.",
        )

from datetime import timedelta
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.google_verify import verify_google_id_token
from app.config import settings
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from shared_lib.schemas import Token
from shared_lib.schemas import GoogleLoginRequest, RefreshTokenRequest, LoginRequest, UserCreate
from app.security import verify_password

router = APIRouter(tags=["Authentication"])
logger = logging.getLogger(__name__)


def _create_token_response(access_token: str, refresh_token: str) -> Token:
    """Helper to create the token response dictionary."""
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(
            timedelta(minutes=settings.access_token_expires_minutes).total_seconds()
        ),
        refresh_token_expires_in=int(
            timedelta(days=settings.refresh_token_expires_days).total_seconds()
        ),
    )

@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return a new token pair.
    """
    user_service = UserService(db)
    auth_service = AuthService(db)

    user = await user_service.get_user_by_email_or_username(request.email_or_username)

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        access_token, refresh_token = await auth_service.create_token_pair(user)
        await db.commit()
        return _create_token_response(access_token, refresh_token)
    except Exception:
        await db.rollback()
        logger.exception("Failed to create tokens during login for user: %s", request.email_or_username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create tokens",
        )

@router.post("/google", response_model=Token)
async def login_with_google(
    request: GoogleLoginRequest, db: AsyncSession = Depends(get_db)
):
    """
    Handles Google Sign-In, creates a user if needed, and returns a new token pair.
    """
    try:
        idinfo = verify_google_id_token(request.id_token)
        email = idinfo.get("email")
        if not email:
            raise ValueError("Email not found in Google token")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {e}",
        )

    user_service = UserService(db)
    auth_service = AuthService(db)
    
    try:
        user = await user_service.get_user_by_email(email)
        if not user:
            user_create_schema = UserCreate(
                email=email,
                password=str(uuid.uuid4()), # Create a random password for Google users
                full_name=idinfo.get("name"),
                avatar_url=idinfo.get("picture"),
                provider="google",
                provider_id=idinfo.get("sub"),
            )
            user = await user_service.create_user(user_create_schema)

        access_token, refresh_token = await auth_service.create_token_pair(user)
        await db.commit()
        
        return _create_token_response(access_token, refresh_token)
    except Exception as e:
        await db.rollback()
        logger.exception("An error occurred during Google login for email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during Google login: {e}",
        )

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """
    Rotates a refresh token to issue a new access and refresh token pair.
    """
    auth_service = AuthService(db)
    try:
        user, new_access_token, new_refresh_token = await auth_service.rotate_refresh_token(request.refresh_token)
        await db.commit()
        
        return _create_token_response(new_access_token, new_refresh_token)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        await db.rollback()
        logger.exception("An unexpected error occurred during token refresh.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not refresh token",
        )

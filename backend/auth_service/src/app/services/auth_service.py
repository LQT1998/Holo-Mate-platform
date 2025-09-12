from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from shared_lib.models.user import User
from shared_lib.models.refresh_token import RefreshToken
from app.security import hash_token, create_refresh_token, create_access_token
from app.config import settings

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_token_pair(self, user: User) -> (str, str):
        """Creates and stores a new refresh token, and returns a new token pair."""
        refresh_token_str = create_refresh_token()
        refresh_token_hash = hash_token(refresh_token_str)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expires_days
        )
        
        new_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=expires_at,
        )
        self.db.add(new_refresh_token)
        
        access_token = create_access_token(subject=user.id)
        
        return access_token, refresh_token_str

    async def rotate_refresh_token(self, old_refresh_token: str) -> (User, str, str):
        """
        Invalidates an old refresh token and issues a new token pair.
        Returns the user, new access token, and new refresh token.
        """
        token_hash = hash_token(old_refresh_token)
        
        token_query = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.db.execute(token_query)
        token = result.scalar_one_or_none()

        if token:
            await self.db.delete(token)
            await self.db.flush() # Mark for deletion

        if not token or token.expires_at < datetime.now(timezone.utc):
            raise ValueError("Invalid or expired refresh token")
            
        user = await self.db.get(User, token.user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        access_token, refresh_token_str = await self.create_token_pair(user)
        
        return user, access_token, refresh_token_str

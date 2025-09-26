# backend/auth_service/src/services/user_service.py

from typing import Optional, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from shared.src.models.user import User
from shared.src.schemas.user import UserCreate  # giả định bạn có schema này
from shared.src.security.utils import get_password_hash


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user with hashed password."""
        hashed_password = get_password_hash(user_create.password)
        user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            is_active=True,  # Default to active
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: Union[UUID, str]) -> Optional[User]:
        """Get a user by UUID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def update_user(self, user_id: Union[UUID, str], updates: dict) -> Optional[User]:
        """Update user fields and persist.

        Args:
            user_id: ID of the user to update
            updates: dict of fields to update (already validated)

        Returns:
            Updated User or None if not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        for field_name, field_value in updates.items():
            # Special handling for password - hash it before storing
            if field_name == "password":
                setattr(user, "hashed_password", get_password_hash(field_value))
            else:
                setattr(user, field_name, field_value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: Union[UUID, str]) -> Optional[User]:
        """Delete a user by UUID and return the deleted user.

        This mimics a soft-delete return signature by returning the removed entity
        so callers can inspect what was deleted.
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        self.db.delete(user)  # delete() is not async
        await self.db.commit()
        return user

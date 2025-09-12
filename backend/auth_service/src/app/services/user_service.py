from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from shared_lib.models.user import User
from shared_lib.schemas import UserCreate, UserUpdate, UserProfileUpdate, UserPreferencesUpdate
from app.security import get_password_hash


class UserService:
    """Service layer for user-related business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: UserCreate) -> User:
        """
        Create a new user.
        Does not commit the transaction.
        """
        existing_user = await self.get_user_by_email(data.email)
        if existing_user:
            raise ConflictError("Email already registered")
            
        hashed_password = get_password_hash(data.password)
        user = User(
            email=data.email,
            hashed_password=hashed_password,
            username=data.username,
            full_name=data.full_name,
            avatar_url=data.avatar_url,
        )
        self.db.add(user)
        await self.db.flush()  # Use flush to assign an ID before returning
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """Get user by ID. Raises NotFoundError if not found."""
        user = await self.db.get(User, user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    async def get_user_by_id_optional(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID. Returns None if not found."""
        return await self.db.get(User, user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email. Returns None if not found."""
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_email_or_username(self, email_or_username: str) -> Optional[User]:
        """Get user by email or username. Returns None if not found."""
        result = await self.db.execute(
            select(User).filter(
                (User.email == email_or_username) | (User.username == email_or_username)
            )
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        """
        Update user profile.
        Does not commit the transaction.
        """
        user = await self.get_user_by_id(user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.flush()
        return user

    async def update_user_profile(self, user: User, data: UserProfileUpdate) -> User:
        """
        Update user profile information.
        Does not commit the transaction.
        """
        # This logic can be expanded, for now it updates basic fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.flush()
        return user

    async def get_user_preferences(self, user: User):
        """Get user preferences."""
        # Assuming preferences are on the user model or a relationship
        return user.preferences

    async def update_user_preferences(self, user: User, data: UserPreferencesUpdate):
        """
        Update user preferences.
        Does not commit the transaction.
        """
        # Assuming preferences is a relationship that can be updated
        preferences = await self.db.get(UserPreference, user.id) # Or however it's linked
        if not preferences:
            preferences = UserPreference(user_id=user.id)
            self.db.add(preferences)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)

        await self.db.flush()
        return preferences

    async def delete_user(self, user_id: uuid.UUID) -> User:
        """
        Soft delete a user by ID.
        Does not commit the transaction.
        """
        user = await self.get_user_by_id(user_id)
        user.is_active = False
        await self.db.flush()
        return user

    async def list_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """List users with optional filtering, pagination, and consistent ordering."""
        query = select(User).order_by(User.created_at.desc())
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_users(self, is_active: Optional[bool] = None) -> int:
        """Count total users with optional filtering, optimized for performance."""
        query = select(func.count()).select_from(User)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        result = await self.db.execute(query)
        return result.scalar_one()

    async def activate_user(self, user_id: uuid.UUID) -> User:
        """
        Activate a user account.
        Does not commit the transaction.
        """
        user = await self.get_user_by_id(user_id)
        if not user.is_active:
            user.is_active = True
            await self.db.flush()
        return user

    async def deactivate_user(self, user_id: uuid.UUID) -> User:
        """
        Deactivate a user account.
        Does not commit the transaction.
        """
        user = await self.get_user_by_id(user_id)
        if user.is_active:
            user.is_active = False
            await self.db.flush()
        return user

    async def search_users_by_name(
        self, 
        name_query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Search users by full name (case-insensitive partial match)."""
        query = select(User).filter(
            User.full_name.ilike(f"%{name_query}%")
        ).order_by(User.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search_users_by_username(
        self, 
        username_query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """Search users by username (case-insensitive partial match)."""
        query = select(User).filter(
            User.username.ilike(f"%{username_query}%")
        ).order_by(User.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()

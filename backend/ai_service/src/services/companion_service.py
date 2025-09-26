"""Business logic for AICompanion CRUD operations.

This module uses SQLAlchemy 2.0 async sessions. In DEV mode, the
API layer keeps returning mock responses; this service is intended
for non-DEV environments.
"""

from __future__ import annotations

from typing import Optional, List
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from shared.src.models.ai_companion import AICompanion
from shared.src.models.character_asset import CharacterAsset
from shared.src.models.voice_profile import VoiceProfile
from ai_service.src.constants.companion_defaults import (
    DEFAULT_CHARACTER_ASSET,
    DEFAULT_VOICE_PROFILE,
)


class CompanionService:
    """Service providing CRUD operations for AICompanion."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_companions(self, user_id: uuid.UUID) -> List[AICompanion]:
        """List all AI companions for a user.
        
        Args:
            user_id: ID of the user whose companions to list
            
        Returns:
            List of AICompanion objects belonging to the user
        """
        stmt = select(AICompanion).where(AICompanion.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_companion_by_id(
        self, user_id: uuid.UUID, companion_id: uuid.UUID
    ) -> Optional[AICompanion]:
        """Get a specific AI companion by ID.
        
        Args:
            user_id: ID of the user who owns the companion
            companion_id: ID of the companion to retrieve
            
        Returns:
            AICompanion object if found, None if not found
        """
        stmt = select(AICompanion).where(
            AICompanion.id == companion_id, AICompanion.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_companion(
        self,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        personality: Optional[dict] = None,
    ) -> AICompanion:
        """Create a new AI companion with default CharacterAsset and VoiceProfile.
        
        Uses atomic transaction to ensure all-or-nothing creation.
        """
        async with self.db.begin():
            # Create companion
            companion = AICompanion(
                user_id=user_id,
                name=name,
                description=description,
                personality=personality,
            )
            self.db.add(companion)
            await self.db.flush()

            # Create default CharacterAsset
            character_asset = CharacterAsset(
                ai_companion_id=companion.id,
                **DEFAULT_CHARACTER_ASSET,
            )
            self.db.add(character_asset)

            # Create default VoiceProfile
            voice_profile = VoiceProfile(
                ai_companion_id=companion.id,
                **DEFAULT_VOICE_PROFILE,
            )
            self.db.add(voice_profile)

        await self.db.refresh(companion)
        return companion

    async def update_companion(
        self,
        user_id: uuid.UUID,
        companion_id: uuid.UUID,
        update_data: dict,
    ) -> Optional[AICompanion]:
        """Update an AI companion with the provided data.
        
        Args:
            user_id: ID of the user who owns the companion
            companion_id: ID of the companion to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated AICompanion object if found and updated, None if not found
            
        Raises:
            HTTPException: 422 if no valid fields provided for update
        """
        # Only allow selected fields
        allowed_fields = {"name", "description", "personality", "status"}
        payload = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No valid fields provided for update. Allowed fields: name, description, personality, status"
            )

        stmt = (
            update(AICompanion)
            .where(AICompanion.id == companion_id, AICompanion.user_id == user_id)
            .values(**payload)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        # Check if any rows were affected
        if result.rowcount == 0:
            return None
            
        return await self.get_companion_by_id(user_id, companion_id)

    async def delete_companion(
        self, user_id: uuid.UUID, companion_id: uuid.UUID
    ) -> bool:
        """Delete an AI companion.
        
        Args:
            user_id: ID of the user who owns the companion
            companion_id: ID of the companion to delete
            
        Returns:
            True if companion was deleted, False if not found
        """
        stmt = delete(AICompanion).where(
            AICompanion.id == companion_id, AICompanion.user_id == user_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        # Use rowcount for better performance, fallback to refetch if needed
        if result.rowcount is not None:
            return result.rowcount > 0
        else:
            # Fallback for drivers that don't support rowcount
            return (await self.get_companion_by_id(user_id, companion_id)) is None



"""
VoiceProfileService - Business logic for managing Voice Profiles
"""

from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.models.voice_profile import VoiceProfile
from shared.src.models.ai_companion import AICompanion
from shared.src.enums.voice_profile_enums import VoiceProfileStatus


class VoiceProfileService:
    """Service for managing voice profiles for AI companions"""
    
    # Allowed fields for voice profile updates
    ALLOWED_UPDATE_FIELDS = {"provider_name", "provider_voice_id", "settings", "status"}
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_voice_profile(
        self, 
        user_id: UUID, 
        companion_id: UUID, 
        provider_name: str, 
        provider_voice_id: str, 
        settings: Optional[dict] = None
    ) -> VoiceProfile:
        """
        Create a new voice profile for a companion.
        
        Args:
            user_id: ID of the user
            companion_id: ID of the AI companion
            provider_name: Name of the voice provider (e.g., "elevenlabs")
            provider_voice_id: Voice ID from the provider
            settings: Optional voice settings (e.g., {"stability": 0.5, "clarity": 0.75})
            
        Returns:
            The created voice profile
            
        Raises:
            HTTPException(400): If companion already has an active voice profile
            HTTPException(404): If companion not found or not owned by user
            HTTPException(422): If required fields are missing
        """
        if not provider_name or not provider_voice_id:
            raise HTTPException(status_code=422, detail="Provider name and voice ID are required")
        
        # Verify companion exists and belongs to user
        companion_stmt = select(AICompanion).where(
            AICompanion.id == companion_id,
            AICompanion.user_id == user_id
        )
        companion_result = await self.db.execute(companion_stmt)
        companion = companion_result.scalars().first()
        if not companion:
            raise HTTPException(status_code=404, detail="Companion not found")
        
        # Check for existing active voice profile
        existing_stmt = select(VoiceProfile).where(
            VoiceProfile.ai_companion_id == companion_id,
            VoiceProfile.status == VoiceProfileStatus.active
        )
        existing_result = await self.db.execute(existing_stmt)
        if existing_result.scalars().first():
            raise HTTPException(status_code=400, detail="Companion already has an active voice profile")
        
        # Create new voice profile
        now = datetime.now(timezone.utc)
        voice_profile = VoiceProfile(
            ai_companion_id=companion_id,
            provider_name=provider_name,
            provider_voice_id=provider_voice_id,
            status=VoiceProfileStatus.active,
            settings=settings or {},
            created_at=now,
            updated_at=now,
        )
        
        self.db.add(voice_profile)
        await self.db.commit()
        await self.db.refresh(voice_profile)
        return voice_profile

    async def get_voice_profile(self, user_id: UUID, profile_id: UUID) -> VoiceProfile:
        """
        Get a specific voice profile by ID, ensuring ownership.
        
        Args:
            user_id: ID of the user requesting the profile
            profile_id: ID of the voice profile to retrieve
            
        Returns:
            The requested voice profile
            
        Raises:
            HTTPException(404): If profile not found or not owned by user
        """
        stmt = (
            select(VoiceProfile)
            .join(AICompanion)
            .where(
                VoiceProfile.id == profile_id,
                AICompanion.user_id == user_id
            )
        )
        result = await self.db.execute(stmt)
        voice_profile = result.scalars().first()
        if not voice_profile:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        return voice_profile

    async def list_voice_profiles(
        self, 
        user_id: UUID, 
        companion_id: Optional[UUID] = None
    ) -> List[VoiceProfile]:
        """
        List voice profiles for a user with optional companion filter.
        
        Args:
            user_id: ID of the user requesting profiles
            companion_id: Optional companion ID to filter by
            
        Returns:
            List of voice profiles for the user
        """
        stmt = (
            select(VoiceProfile)
            .join(AICompanion)
            .where(AICompanion.user_id == user_id)
        )
        
        if companion_id:
            stmt = stmt.where(VoiceProfile.ai_companion_id == companion_id)
        
        stmt = stmt.order_by(VoiceProfile.created_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_voice_profile(
        self, 
        user_id: UUID, 
        profile_id: UUID, 
        update_data: dict
    ) -> VoiceProfile:
        """
        Update a voice profile's information.
        
        Args:
            user_id: ID of the user requesting the update
            profile_id: ID of the voice profile to update
            update_data: Dictionary of fields to update
            
        Returns:
            The updated voice profile
            
        Raises:
            HTTPException(404): If profile not found or not owned by user
            HTTPException(422): If no valid fields to update
        """
        # Filter allowed fields
        update_fields = {k: v for k, v in update_data.items() if k in self.ALLOWED_UPDATE_FIELDS}
        
        if not update_fields:
            raise HTTPException(
                status_code=422, 
                detail=f"No valid fields to update. Allowed fields: {', '.join(self.ALLOWED_UPDATE_FIELDS)}"
            )
        
        # Convert status string to enum if provided
        if "status" in update_fields:
            try:
                update_fields["status"] = VoiceProfileStatus(update_fields["status"])
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {update_fields['status']}")
        
        # Add updated_at timestamp
        update_fields["updated_at"] = datetime.now(timezone.utc)
        
        # Use subquery to check ownership
        ownership_subquery = (
            select(VoiceProfile.id)
            .join(AICompanion, VoiceProfile.ai_companion_id == AICompanion.id)
            .where(VoiceProfile.id == profile_id, AICompanion.user_id == user_id)
        )
        
        stmt = (
            update(VoiceProfile)
            .where(VoiceProfile.id.in_(ownership_subquery))
            .values(**update_fields)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        
        # Return updated voice profile
        return await self.get_voice_profile(user_id, profile_id)

    async def _delete_voice_profile(self, user_id: UUID, profile_id: UUID) -> bool:
        """
        Delete a voice profile permanently (INTERNAL USE ONLY).
        
        This method performs hard delete and should only be used by:
        - Admin operations
        - System cleanup tasks
        - Data migration scripts
        
        For user-facing operations, use archive_voice_profile() instead.
        
        Args:
            user_id: ID of the user requesting deletion
            profile_id: ID of the voice profile to delete
            
        Returns:
            True if profile was deleted
            
        Raises:
            HTTPException(404): If profile not found or not owned by user
        """
        # Use subquery to check ownership
        ownership_subquery = (
            select(VoiceProfile.id)
            .join(AICompanion, VoiceProfile.ai_companion_id == AICompanion.id)
            .where(VoiceProfile.id == profile_id, AICompanion.user_id == user_id)
        )
        
        stmt = delete(VoiceProfile).where(VoiceProfile.id.in_(ownership_subquery))
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        
        return True

    async def delete_voice_profile(self, user_id: UUID, profile_id: UUID) -> bool:
        """
        Delete a voice profile (soft delete - archives the profile).
        
        This is the user-facing delete method that performs soft delete
        by archiving the voice profile instead of permanently removing it.
        
        Args:
            user_id: ID of the user requesting deletion
            profile_id: ID of the voice profile to delete
            
        Returns:
            True if profile was deleted (archived)
            
        Raises:
            HTTPException(404): If profile not found or not owned by user
        """
        # Use archive_voice_profile for soft delete
        await self.archive_voice_profile(user_id, profile_id)
        return True

    async def get_active_voice_profile(self, user_id: UUID, companion_id: UUID) -> Optional[VoiceProfile]:
        """
        Get the currently active voice profile for a companion.
        
        Args:
            user_id: ID of the user
            companion_id: ID of the companion
            
        Returns:
            Active voice profile if found, None otherwise
        """
        stmt = (
            select(VoiceProfile)
            .join(AICompanion)
            .where(
                AICompanion.user_id == user_id,
                VoiceProfile.ai_companion_id == companion_id,
                VoiceProfile.status == VoiceProfileStatus.active
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def set_active_voice_profile(self, user_id: UUID, profile_id: UUID) -> VoiceProfile:
        """
        Set a voice profile as active and deactivate others for the same companion.
        
        Args:
            user_id: ID of the user
            profile_id: ID of the voice profile to activate
            
        Returns:
            The activated voice profile
            
        Raises:
            HTTPException(404): If profile not found or not owned by user
        """
        # First get the profile to ensure ownership and get companion_id
        voice_profile = await self.get_voice_profile(user_id, profile_id)
        
        now = datetime.now(timezone.utc)
        
        # Deactivate all other profiles for this companion
        deactivate_stmt = (
            update(VoiceProfile)
            .where(
                VoiceProfile.ai_companion_id == voice_profile.ai_companion_id,
                VoiceProfile.id != profile_id,
                VoiceProfile.status == VoiceProfileStatus.active
            )
            .values(
                status=VoiceProfileStatus.inactive,
                updated_at=now
            )
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(deactivate_stmt)
        
        # Activate the target profile
        activate_stmt = (
            update(VoiceProfile)
            .where(VoiceProfile.id == profile_id)
            .values(
                status=VoiceProfileStatus.active,
                updated_at=now
            )
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(activate_stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        
        # Return updated voice profile
        return await self.get_voice_profile(user_id, profile_id)

    async def count_voice_profiles(self, user_id: UUID, companion_id: Optional[UUID] = None) -> int:
        """
        Count voice profiles for a user, optionally filtered by companion.
        
        Args:
            user_id: ID of the user
            companion_id: Optional companion ID filter
            
        Returns:
            Number of voice profiles
        """
        stmt = (
            select(func.count(VoiceProfile.id))
            .join(AICompanion)
            .where(AICompanion.user_id == user_id)
        )
        
        if companion_id:
            stmt = stmt.where(VoiceProfile.ai_companion_id == companion_id)
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def get_voice_profile_stats(self, user_id: UUID) -> dict:
        """
        Get voice profile statistics for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with voice profile statistics
        """
        # Count by status - single query with group_by
        status_stmt = (
            select(VoiceProfile.status, func.count(VoiceProfile.id))
            .join(AICompanion)
            .where(AICompanion.user_id == user_id)
            .group_by(VoiceProfile.status)
        )
        status_result = await self.db.execute(status_stmt)
        status_counts = {row[0].value: row[1] for row in status_result.fetchall()}
        
        # Initialize missing statuses with 0
        for status in VoiceProfileStatus:
            if status.value not in status_counts:
                status_counts[status.value] = 0
        
        # Count by provider
        provider_stmt = (
            select(VoiceProfile.provider_name, func.count(VoiceProfile.id))
            .join(AICompanion)
            .where(AICompanion.user_id == user_id)
            .group_by(VoiceProfile.provider_name)
        )
        provider_result = await self.db.execute(provider_stmt)
        provider_counts = {row[0]: row[1] for row in provider_result.fetchall()}
        
        return {
            "total_voice_profiles": sum(status_counts.values()),
            "status_counts": status_counts,
            "provider_counts": provider_counts,
        }

    async def archive_voice_profile(self, user_id: UUID, profile_id: UUID) -> VoiceProfile:
        """
        Archive a voice profile (soft delete).
        
        Args:
            user_id: ID of the user
            profile_id: ID of the voice profile to archive
            
        Returns:
            The archived voice profile
            
        Raises:
            HTTPException(404): If profile not found or not owned by user
        """
        now = datetime.now(timezone.utc)
        # Use subquery to check ownership
        ownership_subquery = (
            select(VoiceProfile.id)
            .join(AICompanion, VoiceProfile.ai_companion_id == AICompanion.id)
            .where(VoiceProfile.id == profile_id, AICompanion.user_id == user_id)
        )
        
        stmt = (
            update(VoiceProfile)
            .where(VoiceProfile.id.in_(ownership_subquery))
            .values(
                status=VoiceProfileStatus.archived,
                updated_at=now
            )
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Voice profile not found")
        
        return await self.get_voice_profile(user_id, profile_id)

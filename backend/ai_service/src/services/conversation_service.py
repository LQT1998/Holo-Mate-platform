"""Service layer for Conversation entity.

Provides business-logic-focused CRUD operations decoupled from API layer.
This module uses SQLAlchemy 2.0 async sessions.
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.models.conversation import Conversation
from ai_service.src.schemas.conversation import ConversationCreate, ConversationUpdate


class ConversationService:
    """Business logic for managing conversations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_conversations(self, user_id: UUID) -> List[Conversation]:
        """Return all conversations owned by the given user."""
        stmt = select(Conversation).where(Conversation.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_conversation_by_id(
        self, user_id: UUID, conversation_id: UUID
    ) -> Conversation:
        """Return a conversation by id if it belongs to the user, else 404."""
        stmt = select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
        result = await self.db.execute(stmt)
        conversation = result.scalars().first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation

    async def create_conversation(
        self, user_id: UUID, data: ConversationCreate
    ) -> Conversation:
        """Create a new conversation owned by the user.

        Notes:
            - Maps companion_id -> ai_companion_id in model
            - Title defaults to "Untitled Conversation" if not provided
            - Status defaults to model default ("active") when not provided
            - metadata and settings are stored as JSON in model (if supported)
        """
        conversation = Conversation(
            user_id=user_id,
            ai_companion_id=data.companion_id,  # Map companion_id -> ai_companion_id
            title=data.title or "Untitled Conversation",
            status=data.status or "active",
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def update_conversation(
        self, user_id: UUID, conversation_id: UUID, data: ConversationUpdate
    ) -> Conversation:
        """Update allowed fields on a conversation owned by the user.

        Allowed fields: title, status
        """
        payload = data.model_dump(exclude_unset=True)
        allowed_fields = {"title", "status"}
        update_data = {k: v for k, v in payload.items() if k in allowed_fields}
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No valid fields to update",
            )

        stmt = (
            update(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        if getattr(result, "rowcount", 0) == 0:
            # If no rows updated, either not found or not owned by user
            raise HTTPException(status_code=404, detail="Conversation not found")
        return await self.get_conversation_by_id(user_id, conversation_id)

    async def delete_conversation(self, user_id: UUID, conversation_id: UUID) -> bool:
        """Delete a conversation if it belongs to the user.

        Returns True if a row was deleted, False otherwise.
        """
        stmt = delete(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return bool(getattr(result, "rowcount", 0))



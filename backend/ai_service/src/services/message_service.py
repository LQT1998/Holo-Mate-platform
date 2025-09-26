"""
MessageService - Business logic for managing Messages in Conversations
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.models.message import Message
from shared.src.models.conversation import Conversation
from shared.src.schemas.message_schema import MessageCreate


class MessageService:
    """Service for managing Messages within Conversations"""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_messages(
        self, 
        user_id: UUID, 
        conversation_id: UUID, 
        page: int = 1, 
        per_page: int = 20
    ) -> List[Message]:
        """
        List messages in a conversation with pagination.
        
        Args:
            user_id: ID of the user requesting messages
            conversation_id: ID of the conversation
            page: Page number (1-based)
            per_page: Number of messages per page
            
        Returns:
            List of messages in the conversation
            
        Raises:
            HTTPException(404): If conversation not found or not owned by user
        """
        # First verify conversation ownership
        conv_stmt = select(Conversation).where(
            Conversation.id == conversation_id, 
            Conversation.user_id == user_id
        )
        conv_result = await self.db.execute(conv_stmt)
        conversation = conv_result.scalars().first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages with pagination
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_message_by_id(self, user_id: UUID, message_id: UUID) -> Message:
        """
        Get a specific message by ID, ensuring ownership through conversation.
        
        Args:
            user_id: ID of the user requesting the message
            message_id: ID of the message to retrieve
            
        Returns:
            The requested message
            
        Raises:
            HTTPException(404): If message not found or not owned by user
        """
        stmt = (
            select(Message)
            .join(Conversation)
            .where(Message.id == message_id, Conversation.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        message = result.scalars().first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message

    async def create_message(
        self, 
        user_id: UUID, 
        conversation_id: UUID, 
        data: MessageCreate
    ) -> Message:
        """
        Create a new message in a conversation.
        
        Args:
            user_id: ID of the user creating the message
            conversation_id: ID of the conversation
            data: Message creation data
            
        Returns:
            The created message
            
        Raises:
            HTTPException(404): If conversation not found or not owned by user
        """
        # Check conversation ownership
        conv_stmt = select(Conversation).where(
            Conversation.id == conversation_id, 
            Conversation.user_id == user_id
        )
        conv_result = await self.db.execute(conv_stmt)
        conversation = conv_result.scalars().first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Create message
        now = datetime.now(timezone.utc)
        message = Message(
            conversation_id=conversation_id,
            role=data.role,
            content=data.content,
            content_type=data.content_type or "text",
            created_at=now,
            updated_at=now,
        )
        self.db.add(message)
        
        # Update conversation's last_message_at and message_count
        conversation.last_message_at = message.created_at
        # Note: message_count will be updated via database trigger or separate query if needed
        
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def delete_message(self, user_id: UUID, message_id: UUID) -> bool:
        """
        Delete a message if it belongs to a conversation owned by the user.
        
        Args:
            user_id: ID of the user requesting deletion
            message_id: ID of the message to delete
            
        Returns:
            True if message was deleted, False if not found or not owned
        """
        stmt = (
            delete(Message)
            .where(Message.id == message_id)
            .where(Message.conversation_id == Conversation.id, Conversation.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return bool(result.rowcount)

    async def count_messages(self, user_id: UUID, conversation_id: UUID) -> int:
        """
        Count total messages in a conversation with ownership check.
        
        Args:
            user_id: ID of the user requesting count
            conversation_id: ID of the conversation
            
        Returns:
            Number of messages in the conversation
            
        Raises:
            HTTPException(404): If conversation not found or not owned by user
        """
        # First verify conversation ownership
        conv_stmt = select(Conversation).where(
            Conversation.id == conversation_id, 
            Conversation.user_id == user_id
        )
        conv_result = await self.db.execute(conv_stmt)
        conversation = conv_result.scalars().first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Count messages
        stmt = select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

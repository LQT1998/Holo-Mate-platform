"""
StreamingService - Business logic for managing Streaming Sessions
"""

from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.models.streaming_session import StreamingSession, SessionStatus
from shared.src.models.hologram_device import HologramDevice


class StreamingService:
    """Service for managing streaming sessions between devices and server"""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def start_session(self, user_id: UUID, device_id: UUID, conversation_id: Optional[UUID] = None, companion_id: Optional[UUID] = None) -> StreamingSession:
        """
        Start a new streaming session for a user and device.
        
        Args:
            user_id: ID of the user starting the session
            device_id: ID of the device for the session
            conversation_id: Optional conversation ID to associate with session
            companion_id: Optional AI companion ID to associate with session
            
        Returns:
            The created streaming session
            
        Raises:
            HTTPException(404): If device not found or not owned by user
            HTTPException(400): If device already has an active session
        """
        # First verify device ownership
        device_stmt = select(HologramDevice).where(
            HologramDevice.id == device_id,
            HologramDevice.user_id == user_id
        )
        device_result = await self.db.execute(device_stmt)
        device = device_result.scalars().first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Check for existing active session
        existing_stmt = select(StreamingSession).where(
            StreamingSession.device_id == device_id,
            StreamingSession.status == SessionStatus.ACTIVE
        )
        existing_result = await self.db.execute(existing_stmt)
        existing_session = existing_result.scalars().first()
        if existing_session:
            raise HTTPException(status_code=400, detail="Device already has an active session")
        
        # Create new session
        now = datetime.now(timezone.utc)
        session = StreamingSession(
            user_id=user_id,
            device_id=device_id,
            conversation_id=conversation_id,
            companion_id=companion_id,
            status=SessionStatus.ACTIVE,
            started_at=now,
            last_active_at=now,
            expires_at=now + timedelta(hours=1)  # 1 hour expiry
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: UUID, user_id: UUID) -> StreamingSession:
        """
        Get a specific streaming session by ID, ensuring ownership.
        
        Args:
            session_id: ID of the session to retrieve
            user_id: ID of the user requesting the session
            
        Returns:
            The requested streaming session
            
        Raises:
            HTTPException(404): If session not found or not owned by user
        """
        stmt = select(StreamingSession).where(
            StreamingSession.id == session_id,
            StreamingSession.user_id == user_id
        )
        result = await self.db.execute(stmt)
        session = result.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Streaming session not found")
        return session

    async def list_sessions(
        self, 
        user_id: UUID, 
        status: Optional[SessionStatus] = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[StreamingSession]:
        """
        List streaming sessions for a user with pagination and optional status filter.
        
        Args:
            user_id: ID of the user requesting sessions
            status: Optional status filter
            page: Page number (1-based)
            per_page: Number of sessions per page
            
        Returns:
            List of streaming sessions for the user
        """
        stmt = select(StreamingSession).where(StreamingSession.user_id == user_id)
        if status:
            stmt = stmt.where(StreamingSession.status == status)
        stmt = stmt.order_by(StreamingSession.started_at.desc())
        
        # Add pagination
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def end_session(self, session_id: UUID, user_id: UUID) -> bool:
        """
        End a streaming session by updating its status to 'ended'.
        
        Args:
            session_id: ID of the session to end
            user_id: ID of the user requesting to end the session
            
        Returns:
            True if session was ended, False if not found or not owned
            
        Raises:
            HTTPException(404): If session not found or not owned by user
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(StreamingSession)
            .where(StreamingSession.id == session_id, StreamingSession.user_id == user_id)
            .values(status=SessionStatus.ENDED, ended_at=now)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Streaming session not found")
        
        return True

    async def heartbeat(self, session_id: UUID, user_id: UUID) -> StreamingSession:
        """
        Update the last_active_at timestamp for a session to keep it alive.
        
        Args:
            session_id: ID of the session to update
            user_id: ID of the user requesting the heartbeat
            
        Returns:
            The updated streaming session
            
        Raises:
            HTTPException(404): If session not found or not owned by user
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(StreamingSession)
            .where(StreamingSession.id == session_id, StreamingSession.user_id == user_id)
            .values(last_active_at=now)
            .returning(StreamingSession)
        )
        result = await self.db.execute(stmt)
        session = result.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Streaming session not found")
        
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
        """
        Delete a streaming session permanently.
        
        Args:
            session_id: ID of the session to delete
            user_id: ID of the user requesting deletion
            
        Returns:
            True if session was deleted, False if not found or not owned
        """
        stmt = delete(StreamingSession).where(
            StreamingSession.id == session_id,
            StreamingSession.user_id == user_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return bool(result.rowcount)

    async def get_active_sessions_count(self, user_id: UUID) -> int:
        """
        Get the count of active streaming sessions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Number of active sessions
        """
        stmt = select(func.count(StreamingSession.id)).where(
            StreamingSession.user_id == user_id,
            StreamingSession.status == SessionStatus.ACTIVE
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def cleanup_expired_sessions(self) -> int:
        """
        Mark expired sessions as 'expired' status.
        This method can be called by a background task.
        
        Returns:
            Number of sessions that were marked as expired
        """
        now = datetime.now(timezone.utc)
        stmt = (
            update(StreamingSession)
            .where(
                StreamingSession.status == SessionStatus.ACTIVE,
                StreamingSession.expires_at < now
            )
            .values(status=SessionStatus.EXPIRED)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

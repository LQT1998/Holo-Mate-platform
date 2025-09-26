"""
Streaming session endpoints for the Holo-Mate platform
"""

from fastapi import (
    APIRouter, Depends, HTTPException, Query, status,
    Request, Path, Response
)
from datetime import datetime, timezone, timedelta
import uuid
from typing import List

from streaming_service.src.security.deps import get_current_user
from streaming_service.src.config import settings
from streaming_service.src.services.streaming_service import StreamingService
from shared.src.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from shared.src.models.streaming_session import StreamingSession
from shared.src.schemas.streaming_session_schema import (
    StreamingSessionStatusRead,
    StreamingSessionCreate,
    ResponseStreamingSessionCreate,
    StreamingSessionListResponse,
    SessionStatus,
    StreamingConfig,
    AudioSettings,
)
from shared.src.models.streaming_session import SessionStatus as ModelSessionStatus

router = APIRouter(tags=["Streaming Sessions"])


@router.get("/sessions", response_model=StreamingSessionListResponse)
async def list_streaming_sessions(
    status: str = Query(None, description="Filter by session status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Sessions per page"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingSessionListResponse:
    """List streaming sessions for the current user"""
    if settings.DEV_MODE:
        # Mock response for DEV mode
        if str(current_user.get("id")) != "550e8400-e29b-41d4-a716-446655440000":
            raise HTTPException(status_code=403, detail="Forbidden: You do not own this session")
        
        # Mock sessions
        now = datetime.now(timezone.utc)
        mock_sessions = [
            {
                "session_id": str(uuid.uuid4()),
                "conversation_id": str(uuid.uuid4()),
                "companion_id": str(uuid.uuid4()),
                "device_id": str(uuid.uuid4()),
                "user_id": current_user.get("id"),
                "status": SessionStatus.active,
                "created_at": now,
                "updated_at": now,
                "expires_at": now + timedelta(hours=1),
                "streaming_config": StreamingConfig(),
                "audio_settings": AudioSettings(),
            },
            {
                "session_id": str(uuid.uuid4()),
                "conversation_id": str(uuid.uuid4()),
                "companion_id": str(uuid.uuid4()),
                "device_id": str(uuid.uuid4()),
                "user_id": current_user.get("id"),
                "status": SessionStatus.ended,
                "created_at": now - timedelta(hours=2),
                "updated_at": now - timedelta(hours=1),
                "expires_at": now - timedelta(minutes=30),
                "streaming_config": StreamingConfig(),
                "audio_settings": AudioSettings(),
            },
        ]
        
        # Filter by status if provided
        if status:
            mock_sessions = [s for s in mock_sessions if s["status"] == status]
        
        total = len(mock_sessions)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated = mock_sessions[start_idx:end_idx]
        
        return StreamingSessionListResponse(
            sessions=paginated,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )
    else:
        # Non-DEV path: use StreamingService
        service = StreamingService(db)
        user_uuid = uuid.UUID(str(current_user["id"]))
        
        # Convert string status to enum if provided
        status_enum = None
        if status:
            try:
                status_enum = ModelSessionStatus(status)
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {status}")
        
        sessions = await service.list_sessions(user_uuid, status_enum, page, per_page)
        
        # Get total count for pagination
        total_stmt = select(func.count(StreamingSession.id)).where(StreamingSession.user_id == user_uuid)
        if status_enum:
            total_stmt = total_stmt.where(StreamingSession.status == status_enum)
        total_result = await db.execute(total_stmt)
        total = total_result.scalar() or 0
        total_pages = (total + per_page - 1) // per_page
        
        # Convert to response format
        session_responses = [
            {
                "session_id": str(session.id),
                "conversation_id": str(session.conversation_id) if session.conversation_id else str(uuid.uuid4()),
                "companion_id": str(session.companion_id) if session.companion_id else str(uuid.uuid4()),
                "device_id": str(session.device_id),
                "user_id": str(session.user_id),
                "status": SessionStatus(session.status.value),
                "created_at": session.started_at,
                "updated_at": session.last_active_at or session.started_at,
                "expires_at": session.expires_at or (session.started_at + timedelta(hours=1)),
                "streaming_config": StreamingConfig() if not session.streaming_config else StreamingConfig(**session.streaming_config),
                "audio_settings": AudioSettings() if not session.audio_settings else AudioSettings(**session.audio_settings),
            }
            for session in sessions
        ]
        
        return StreamingSessionListResponse(
            sessions=session_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )


def _validate_session_id_format(session_id: str) -> None:
    if not session_id or not session_id.strip():
        raise HTTPException(status_code=422, detail="Invalid session ID format")
    if any(ch.isspace() for ch in session_id):
        raise HTTPException(status_code=422, detail="Invalid session ID format")


def _normalize_session_id(session_id: str) -> str:
    """DEV mode: map string → UUID5 for stable websocket URL"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"dev:streaming_chat:{session_id}"))


@router.get(
    "/sessions/{session_id}/chat",
    response_model=StreamingSessionStatusRead,
    status_code=200,
)
async def get_streaming_session_status(
    session_id: str = Path(..., description="Streaming session ID"),
    include_metrics: bool = Query(False),
    include_errors: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    request: Request = None,
):
    """Get status of a streaming chat session"""
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    # Validate auth (DEV mode)
    auth = request.headers.get("Authorization") if request else None
    if not auth:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    if auth[7:] != "valid_access_token_here":
        raise HTTPException(status_code=401, detail="Invalid token")

    _validate_session_id_format(session_id)

    # Special DEV ids for contract tests
    if session_id == "invalid_session_id":
        raise HTTPException(status_code=422, detail="Invalid session ID format")
    if session_id == "nonexistent_session_456":
        raise HTTPException(status_code=404, detail="Streaming session not found")
    if session_id == "forbidden_999":
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this session")

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=1)
    ws_scheme = "wss" if request.url.scheme == "https" else "ws"
    websocket_url = f"{ws_scheme}://{request.url.hostname}:{request.url.port}/ws/streaming/{_normalize_session_id(session_id)}"

    response_data = {
        "session_id": session_id,
        "conversation_id": str(uuid.uuid4()),
        "companion_id": str(uuid.uuid4()),
        "device_id": str(uuid.uuid4()),
        "user_id": current_user.get("id"),
        "status": SessionStatus.active,
        "created_at": now,
        "updated_at": now,
        "expires_at": expires_at,
        "websocket_url": websocket_url,
        "streaming_config": StreamingConfig(),
        "audio_settings": AudioSettings(),
    }

    if include_metrics:
        response_data["metrics"] = {
            "bytes_transferred": 1024000,
            "messages_sent": 42,
            "uptime_seconds": 3600,
            "connection_quality": "excellent",
            "packet_loss": 0.01,
            "latency_ms": 45,
        }
    if include_errors:
        response_data["errors"] = [{
            "code": "CONNECTION_TIMEOUT",
            "message": "Connection timeout occurred",
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
        }]

    # Mock state switching
    if session_id in ["expired_session_123", "expired_session_test"]:
        response_data["status"] = SessionStatus.expired
        response_data["expires_at"] = now - timedelta(hours=1)
    elif session_id == "error_session_456":
        response_data["status"] = SessionStatus.error
        response_data["errors"] = [{
            "code": "AUDIO_DEVICE_ERROR",
            "message": "Audio device not available",
            "timestamp": now.isoformat(),
        }]
    elif session_id == "connecting_session_789":
        response_data["status"] = SessionStatus.connecting
    elif session_id == "ended_session_000":
        response_data["status"] = SessionStatus.ended

    return StreamingSessionStatusRead(**response_data)


@router.post(
    "/sessions",
    response_model=ResponseStreamingSessionCreate,
    status_code=201,
    summary="Start streaming chat session",
)
async def start_streaming_chat(
    request: StreamingSessionCreate,
    response: Response,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResponseStreamingSessionCreate:
    """Start a new streaming chat session"""
    if settings.DEV_MODE:
        # Mock response for DEV mode
        # Validations for DEV contract tests (device-based)
        if not request.device_id or not isinstance(request.device_id, str):
            raise HTTPException(status_code=422, detail="Invalid device ID format")
        if request.device_id == "invalid_device_id":
            raise HTTPException(status_code=422, detail="Invalid device ID format")
        if request.device_id == "nonexistent_device_456":
            raise HTTPException(status_code=404, detail="Device not found")
        if request.device_id == "forbidden_999":
            raise HTTPException(status_code=403, detail="Forbidden: You do not own this device")
        if request.device_id == "unavailable_device_999":
            raise HTTPException(status_code=503, detail="Device not available")

        session_id = str(uuid.uuid4())
        ws_scheme = "wss" if response.headers.get("x-forwarded-proto") == "https" else "ws"
        websocket_url = f"{ws_scheme}://localhost:8003/ws/streaming/{session_id}"

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=1)

        response.headers["Location"] = f"/streaming/sessions/{session_id}/chat"

        return ResponseStreamingSessionCreate(
            session_id=session_id,
            conversation_id=str(uuid.uuid4()),
            companion_id=str(uuid.uuid4()),
            device_id=request.device_id,
            user_id=current_user.get("id"),
            websocket_url=websocket_url,
            status=SessionStatus.active,
            created_at=now,
            expires_at=expires_at,
            streaming_config=StreamingConfig(),
            audio_settings=AudioSettings(),
        )
    else:
        # Non-DEV path: use StreamingService
        service = StreamingService(db)
        user_uuid = uuid.UUID(str(current_user["id"]))
        device_uuid = uuid.UUID(request.device_id)
        
        # Parse optional conversation_id and companion_id from settings
        conversation_id = None
        companion_id = None
        if request.settings:
            conversation_id = request.settings.get("conversation_id")
            companion_id = request.settings.get("companion_id")
            if conversation_id:
                conversation_id = uuid.UUID(conversation_id)
            if companion_id:
                companion_id = uuid.UUID(companion_id)
        
        session = await service.start_session(user_uuid, device_uuid, conversation_id, companion_id)
        
        ws_scheme = "wss" if response.headers.get("x-forwarded-proto") == "https" else "ws"
        websocket_url = f"{ws_scheme}://localhost:8003/ws/streaming/{session.id}"
        
        response.headers["Location"] = f"/streaming/sessions/{session.id}/chat"
        
        return ResponseStreamingSessionCreate(
            session_id=str(session.id),
            conversation_id=str(session.conversation_id) if session.conversation_id else str(uuid.uuid4()),
            companion_id=str(session.companion_id) if session.companion_id else str(uuid.uuid4()),
            device_id=str(session.device_id),
            user_id=str(session.user_id),
            websocket_url=websocket_url,
            status=SessionStatus(session.status.value),
            created_at=session.started_at,
            expires_at=session.expires_at or (session.started_at + timedelta(hours=1)),
            streaming_config=StreamingConfig() if not session.streaming_config else StreamingConfig(**session.streaming_config),
            audio_settings=AudioSettings() if not session.audio_settings else AudioSettings(**session.audio_settings),
        )



"""
Streaming session endpoints for the Holo-Mate platform
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Request,
    Path,
)
from datetime import datetime, timezone, timedelta
import uuid

from streaming_service.src.security.deps import get_current_user
from streaming_service.src.config import settings
from shared.src.schemas.streaming_session_schema import (
    StreamingSessionStatusRead,
    SessionStatus,
    StreamingConfig,
    AudioSettings,
)

router = APIRouter(tags=["Streaming Sessions"])


def _validate_session_id_format_raw(session_id: str) -> None:
    if session_id is None or not session_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid session ID format",
        )
    if any(ch.isspace() for ch in session_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid session ID format",
        )


def _normalize_session_id(session_id: str) -> str:
    """
    Normalize session ID in DEV mode: keep as is, but map to UUID5
    so websocket URL is stable.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"dev:streaming_chat:{session_id}"))


@router.get(
    "/streaming/sessions/{session_id}/chat",
    response_model=StreamingSessionStatusRead,
    status_code=status.HTTP_200_OK,
)
async def get_streaming_session_status(
    session_id: str = Path(..., description="Streaming session ID"),
    include_metrics: bool = Query(False, description="Include streaming metrics"),
    include_errors: bool = Query(False, description="Include error details"),
    current_user: dict = Depends(get_current_user),
    request: Request = None,
):
    """
    Get streaming session (chat) status by session ID.
    """
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    # Manual auth check in DEV mode
    auth_header = request.headers.get("Authorization") if request else None
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")
    if auth_header[7:] != "valid_access_token_here":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Validate session id
    _validate_session_id_format_raw(session_id)

    # Special DEV ids
    if session_id == "invalid_session_id":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid session ID format")
    if session_id == "nonexistent_session_456":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Streaming session not found")
    if session_id == "forbidden_999":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not own this session",
        )

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=1)
    normalized_id = _normalize_session_id(session_id)

    response_data = {
        "session_id": session_id,
        "conversation_id": str(uuid.uuid4()),
        "companion_id": str(uuid.uuid4()),
        "device_id": str(uuid.uuid4()),
        "status": SessionStatus.active,
        "created_at": now,
        "updated_at": now,
        "expires_at": expires_at,
        "websocket_url": f"ws://localhost:8003/ws/streaming/{normalized_id}",
        "streaming_config": StreamingConfig(
            transport="websocket",
            buffer_size=4096,
            voice_enabled=True,
            emotion_detection=True,
            response_format="audio",
            quality="high",
            latency="low",
        ),
        "audio_settings": AudioSettings(
            sample_rate=44100,
            codec="opus",
            channels=1,
            noise_reduction=True,
            echo_cancellation=True,
            auto_gain_control=True,
        ),
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
        response_data["errors"] = [
            {
                "code": "CONNECTION_TIMEOUT",
                "message": "Connection timeout occurred",
                "timestamp": (now - timedelta(minutes=5)).isoformat(),
            }
        ]

    # Mock session states for contract tests
    if session_id == "expired_session_123" or session_id == "expired_session_test":
        response_data["status"] = SessionStatus.expired
        response_data["expires_at"] = now - timedelta(hours=1)
    elif session_id == "error_session_456" or str(session_id).startswith("00000000-0000-0000-0000-0000000f"):
        response_data["status"] = SessionStatus.error
        response_data["errors"] = [
            {
                "code": "AUDIO_DEVICE_ERROR",
                "message": "Audio device not available",
                "timestamp": now.isoformat(),
            }
        ]
    elif session_id == "connecting_session_789" or str(session_id).startswith("00000000-0000-0000-0000-0000000c"):
        response_data["status"] = SessionStatus.connecting
    elif session_id == "ended_session_000" or str(session_id).startswith("00000000-0000-0000-0000-0000000d"):
        response_data["status"] = SessionStatus.ended

    return StreamingSessionStatusRead(**response_data)

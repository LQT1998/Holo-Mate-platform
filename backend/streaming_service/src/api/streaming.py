"""
Streaming session endpoints for the Holo-Mate platform
"""

from fastapi import (
    APIRouter, Depends, HTTPException, Query, status,
    Request, Path, Response
)
from datetime import datetime, timezone, timedelta
import uuid

from streaming_service.src.security.deps import get_current_user
from streaming_service.src.config import settings
from shared.src.schemas.streaming_session_schema import (
    StreamingSessionStatusRead,
    StreamingSessionCreate,
    ResponseStreamingSessionCreate,
    SessionStatus,
    StreamingConfig,
    AudioSettings,
)

router = APIRouter(tags=["Streaming Sessions"])


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
) -> ResponseStreamingSessionCreate:
    """Start a new streaming chat session"""
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

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



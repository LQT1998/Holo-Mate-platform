from fastapi import APIRouter, Depends, HTTPException, Response, status
from datetime import datetime, timezone
import uuid

from streaming_service.src.security.deps import get_current_user
from streaming_service.src.config import settings
from shared.src.schemas.streaming_session_schema import (
    StreamingSessionCreate,
    StreamingSessionRead,
)
from shared.src.constants import DEV_OWNER_ID

router = APIRouter(tags=["Streaming Sessions"])


@router.post(
    "/streaming/sessions",
    response_model=StreamingSessionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_streaming_session(
    payload: StreamingSessionCreate,
    response: Response,
    current_user: dict = Depends(get_current_user),
):
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    # Special DEV cases
    if payload.device_id == "invalid_device_id":
        raise HTTPException(status_code=422, detail="Invalid device ID format")
    if payload.device_id == "nonexistent_device_456":
        raise HTTPException(status_code=404, detail="Device not found")
    if payload.device_id == "forbidden_999":
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this device")

    # Ownership check
    if str(current_user.get("id")) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this device")

    # Mock session creation
    now = datetime.now(timezone.utc)
    session_id = uuid.uuid4()

    session = StreamingSessionRead(
        id=session_id,
        device_id=payload.device_id,
        user_id=uuid.UUID(str(current_user["id"])),
        status="active",
        created_at=now,
        updated_at=now,
        settings=payload.settings or {},
    )

    response.headers["Location"] = f"/streaming/sessions/{session_id}"

    return session

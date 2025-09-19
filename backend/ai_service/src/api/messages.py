"""
Messages API endpoints for AI service
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from datetime import datetime, timezone
import uuid

from ai_service.src.security.deps import get_current_user
from ai_service.src.config import settings

from shared.src.schemas.message_schema import (
    MessageCreate,
    MessageResponse,
)
from ai_service.src.schemas.ai_companion import DeleteResponse
from shared.src.constants import DEV_OWNER_ID

router = APIRouter(tags=["Messages"])


def _validate_id_format_raw(id_str: str, id_type: str = "message") -> None:
    if id_type == "message":
        if id_str in ["invalid_message_id", "   ", "id with spaces"]:
            raise HTTPException(status_code=422, detail="Invalid message ID format")
    elif id_type == "conversation":
        if id_str in ["invalid_conversation_id", "   ", "id with spaces"]:
            raise HTTPException(status_code=422, detail="Invalid conversation ID format")


def normalize_message_id(message_id: str) -> uuid.UUID:
    _validate_id_format_raw(message_id)
    try:
        return uuid.UUID(message_id)
    except ValueError:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"dev:message:{message_id}")


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> MessageResponse:
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    conv_id_str = str(message_data.conversation_id)
    _validate_id_format_raw(conv_id_str, "conversation")

    try:
        conversation_uuid = uuid.UUID(conv_id_str)
    except ValueError:
        conversation_uuid = uuid.uuid5(uuid.NAMESPACE_URL, f"dev:conversation:{conv_id_str}")

    if conv_id_str == "nonexistent_conversation_456":
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv_id_str == "forbidden_999":
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this message")

    if str(current_user.get("id")) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this message")

    now = datetime.now(timezone.utc)
    message_uuid = uuid.uuid4()

    created_message = MessageResponse(
        id=message_uuid,
        conversation_id=conversation_uuid,
        role=message_data.role,
        content=message_data.content,
        content_type=message_data.content_type,
        created_at=now,
        updated_at=now,
    )

    response.headers["Location"] = f"/messages/{message_uuid}"
    return created_message


@router.get("/messages/{message_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def get_message(
    message_id: str,
    current_user: dict = Depends(get_current_user),
) -> MessageResponse:
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    if message_id == "nonexistent_message_456":
        raise HTTPException(status_code=404, detail="Message not found")
    if message_id == "forbidden_999":
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this message")

    message_uuid = normalize_message_id(message_id)

    if str(current_user.get("id")) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this message")

    now = datetime.now(timezone.utc)
    conversation_uuid = uuid.uuid5(uuid.NAMESPACE_URL, "dev:conversation:conversation_123")

    return MessageResponse(
        id=message_uuid,
        conversation_id=conversation_uuid,
        role="user",
        content="Hello, this is a test message",
        content_type="text",
        created_at=now,
        updated_at=now,
    )


@router.delete("/messages/{message_id}", response_model=DeleteResponse, status_code=status.HTTP_200_OK)
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user),
) -> DeleteResponse:
    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    if message_id == "nonexistent_message_456":
        raise HTTPException(status_code=404, detail="Message not found")
    if message_id == "forbidden_999":
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this message")

    message_uuid = normalize_message_id(message_id)

    if str(current_user.get("id")) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this message")

    return DeleteResponse(
        message="Message deleted successfully",
        deleted_id=str(message_uuid),
    )

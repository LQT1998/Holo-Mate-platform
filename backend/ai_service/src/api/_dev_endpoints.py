from __future__ import annotations
from fastapi import APIRouter, status
from backend.ai_service.src.realtime.events import publish_message_created


router = APIRouter()


@router.post("/_dev/conversations/{conversation_id}/messages", status_code=status.HTTP_202_ACCEPTED)
async def dev_broadcast_message(conversation_id: str, payload: dict):
    await publish_message_created(conversation_id, payload)
    return {"ok": True}



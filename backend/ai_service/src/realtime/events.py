from __future__ import annotations
from typing import Dict, Any
from backend.ai_service.src.realtime.connection_manager import manager
from backend.ai_service.src.realtime.bus import bus


async def publish_message_created(conversation_id: str, message: Dict[str, Any]) -> int:
    event = {"type": "message.new", "data": message, "cid": conversation_id}
    await manager.broadcast_to_conversation(conversation_id, event)
    await bus.publish_conversation(conversation_id, event)
    return 1



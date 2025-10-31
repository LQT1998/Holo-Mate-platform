from __future__ import annotations
from datetime import datetime, timezone


class ReadService:
    async def mark_read(self, user_id: str, conversation_id: str, message_id: str) -> dict:
        # TODO: persist to database (message_read + upsert conversation_read_state)
        return {
            "user_id": user_id,
            "cid": conversation_id,
            "mid": message_id,
            "read_at": datetime.now(tz=timezone.utc).isoformat(),
        }


read_service = ReadService()



from __future__ import annotations
import asyncio
import json
from typing import Optional
from backend.ai_service.src.realtime.settings import get_settings
from backend.ai_service.src.realtime.connection_manager import manager

try:
    from redis.asyncio import from_url as redis_from_url  # type: ignore
except Exception:  # pragma: no cover
    redis_from_url = None


class NoopBus:
    async def ensure_started(self) -> None:  # pragma: no cover - trivial
        return

    async def publish_conversation(self, cid: str, event: dict) -> None:
        await manager.broadcast_to_conversation(cid, event)


class RedisBus:
    def __init__(self, url: str) -> None:
        self._url = url
        self._redis = None
        self._pub = None
        self._sub = None
        self._task: Optional[asyncio.Task] = None
        self._started = asyncio.Event()

    async def ensure_started(self) -> None:
        if self._task:
            return
        self._redis = redis_from_url(self._url, encoding="utf-8", decode_responses=True)  # type: ignore
        self._pub = self._redis
        self._sub = self._redis.pubsub()
        await self._sub.psubscribe("ws:conversation:*")
        self._task = asyncio.create_task(self._run())
        self._started.set()

    async def _run(self) -> None:
        assert self._sub is not None
        async for msg in self._sub.listen():
            if msg is None:
                continue
            if msg.get("type") not in ("pmessage", "message"):
                continue
            data = msg.get("data")
            try:
                event = json.loads(data)
            except Exception:
                continue
            cid = event.get("cid") or (event.get("data") or {}).get("cid")
            if cid:
                await manager.broadcast_to_conversation(cid, event)

    async def publish_conversation(self, cid: str, event: dict) -> None:
        assert self._pub is not None
        await self._pub.publish(f"ws:conversation:{cid}", json.dumps(event))


_settings = get_settings()
if _settings.redis_url and redis_from_url is not None:
    bus = RedisBus(_settings.redis_url)
else:
    bus = NoopBus()



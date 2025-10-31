from __future__ import annotations
import asyncio
import logging
from collections import defaultdict
from typing import Any, Dict, Set, Optional
from fastapi import WebSocket
from backend.ai_service.src.realtime.metrics import on_connect, on_disconnect, count_drop

logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, ws: WebSocket, user_id: str | None = None) -> None:
        self.ws = ws
        self.user_id = user_id
        self.rooms: Set[str] = set()
        self.queue: "asyncio.Queue[Any]" = asyncio.Queue(maxsize=512)
        self._writer_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._writer_task = asyncio.create_task(self._writer())

    async def _writer(self) -> None:
        try:
            while True:
                msg = await self.queue.get()
                await self.ws.send_json(msg)
        except Exception as exc:  # pragma: no cover
            logger.debug("WS writer stopped: %s", exc)

    async def send(self, event: Any) -> None:
        try:
            self.queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning("Dropping WS message due to full queue")  # pragma: no cover

    async def close(self) -> None:
        if self._writer_task:
            self._writer_task.cancel()
            try:
                await self._writer_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass


class ConnectionManager:
    def __init__(self) -> None:
        self._by_room: Dict[str, Set[Connection]] = defaultdict(set)
        self._by_user: Dict[str, Set[Connection]] = defaultdict(set)
        self._by_ws: Dict[WebSocket, Connection] = {}
        self._lock = asyncio.Lock()

    async def register(self, ws: WebSocket, user_id: str | None) -> Connection:
        conn = Connection(ws, user_id=user_id)
        async with self._lock:
            self._by_ws[ws] = conn
            if user_id:
                self._by_user[user_id].add(conn)
        await conn.start()
        try:
            on_connect()
        except Exception:
            pass
        return conn

    async def join_rooms(self, ws: WebSocket, cids: Set[str]) -> None:
        async with self._lock:
            conn = self._by_ws.get(ws)
            if not conn:
                return
            for cid in cids:
                conn.rooms.add(cid)
                self._by_room[cid].add(conn)

    async def leave_all(self, ws: WebSocket) -> Set[str]:
        left: Set[str] = set()
        async with self._lock:
            conn = self._by_ws.get(ws)
            if not conn:
                return left
            for cid in list(conn.rooms):
                left.add(cid)
                conn.rooms.discard(cid)
                self._by_room[cid].discard(conn)
            return left

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            conn = self._by_ws.pop(ws, None)
            if not conn:
                return
            for cid in list(conn.rooms):
                self._by_room[cid].discard(conn)
            if conn.user_id:
                self._by_user[conn.user_id].discard(conn)
        if conn:
            await conn.close()
        try:
            on_disconnect()
        except Exception:
            pass

    async def broadcast_to_conversation(self, cid: str, event: Dict[str, Any], exclude: Optional[WebSocket] = None) -> int:
        recipients = 0
        conns = list(self._by_room.get(cid, set()))
        for conn in conns:
            if exclude is not None and conn.ws is exclude:
                continue
            await conn.send(event)
            recipients += 1
        return recipients

    async def broadcast_to_user(self, user_id: str, event: Dict[str, Any], exclude: Optional[WebSocket] = None) -> int:
        recipients = 0
        for conn in list(self._by_user.get(user_id, set())):
            if exclude is not None and conn.ws is exclude:
                continue
            await conn.send(event)
            recipients += 1
        return recipients


manager = ConnectionManager()



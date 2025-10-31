import asyncio
import pytest

from backend.ai_service.src.realtime.connection_manager import ConnectionManager


class DummyWS:
    def __init__(self):
        self.sent = []

    async def send_json(self, msg):
        self.sent.append(msg)


@pytest.mark.asyncio
async def test_connect_join_broadcast():
    mgr = ConnectionManager()
    ws1 = DummyWS()
    ws2 = DummyWS()

    await mgr.register(ws1, user_id="u1")
    await mgr.register(ws2, user_id="u2")

    await mgr.join_rooms(ws1, {"c-1"})
    await mgr.join_rooms(ws2, {"c-1"})

    event = {"type": "hello"}
    n = await mgr.broadcast_to_conversation("c-1", event)
    assert n == 2


@pytest.mark.asyncio
async def test_disconnect_removes_from_rooms_and_users():
    mgr = ConnectionManager()
    ws1 = DummyWS()
    await mgr.register(ws1, user_id="u1")
    await mgr.join_rooms(ws1, {"c-1", "c-2"})
    await mgr.disconnect(ws1)
    n = await mgr.broadcast_to_conversation("c-1", {"type": "x"})
    assert n == 0



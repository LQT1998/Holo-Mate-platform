from __future__ import annotations
import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.ai_service.src.realtime.connection_manager import manager
from backend.ai_service.src.realtime.auth import auth_ws
from backend.ai_service.src.realtime.rate_limit import TokenBucket
from backend.ai_service.src.realtime.settings import get_settings
from backend.ai_service.src.realtime.bus import bus


router = APIRouter()


def _ts() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


async def _heartbeat(ws: WebSocket, interval: int, miss_allowed: int) -> None:
    misses = 0
    try:
        while True:
            await asyncio.sleep(interval)
            try:
                await ws.send_json({"type": "ping", "ts": _ts()})
            except Exception:
                misses += 1
                if misses > miss_allowed:
                    await ws.close(code=1011)
                    break
    except asyncio.CancelledError:
        return


@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    settings = get_settings()

    subproto_hdr = websocket.headers.get("sec-websocket-protocol") or websocket.headers.get("Sec-WebSocket-Protocol")
    subprotocol = None
    if subproto_hdr:
        offered = [p.strip() for p in subproto_hdr.split(",") if p.strip()]
        for p in offered:
            if p in settings.subprotocols:
                subprotocol = p
                break
    await websocket.accept(subprotocol=subprotocol)

    claims = await auth_ws(websocket)
    if not claims:
        return

    user_id = claims.get("user_id") or claims.get("sub")

    await manager.register(websocket, user_id=user_id)
    await bus.ensure_started()

    limiter = TokenBucket.per_10s(settings.max_msg_per_10s)
    hb = asyncio.create_task(_heartbeat(websocket, settings.ping_interval_sec, settings.ping_miss_allowed))

    try:
        while True:
            raw = await websocket.receive_text()
            if len(raw.encode("utf-8")) > settings.max_frame_bytes:
                await websocket.send_json({"type": "error", "error": "frame_too_large"})
                await websocket.close(code=1009)
                break

            if not limiter.consume(1.0):
                await websocket.send_json({"type": "error", "error": "rate_limited"})
                await websocket.close(code=4408)
                break

            try:
                evt: dict[str, Any] = json.loads(raw)
            except Exception:
                await websocket.send_json({"type": "error", "error": "bad_json"})
                continue

            etype = evt.get("type")
            if etype == "presence.join":
                data = evt.get("data") or {}
                cids = set(data.get("cids") or [])
                if not cids:
                    await websocket.send_json({"type": "error", "error": "missing_cids"})
                    continue
                await manager.join_rooms(websocket, cids)
                for cid in cids:
                    await manager.broadcast_to_conversation(cid, {"type": "presence.join", "data": {"cid": cid}}, exclude=websocket)
                await websocket.send_json({"type": "presence.join", "data": {"cids": list(cids)}})

            elif etype == "message.new":
                cid = evt.get("cid") or (evt.get("data") or {}).get("cid")
                data = evt.get("data") or {}
                content = data.get("content", "")
                if not cid or not content or len(content) > 4000:
                    await websocket.send_json({"type": "error", "error": "invalid_message"})
                    continue
                ack = {"type": "message.ack", "cid": cid, "data": {"ok": True}}
                await websocket.send_json(ack)
                event = {"type": "message.new", "data": data, "cid": cid}
                await manager.broadcast_to_conversation(cid, event, exclude=None)
                await bus.publish_conversation(cid, event)

            elif etype == "typing":
                cid = evt.get("cid") or (evt.get("data") or {}).get("cid")
                is_typing = bool((evt.get("data") or {}).get("is_typing", True))
                if cid:
                    await manager.broadcast_to_conversation(cid, {"type": "typing", "data": {"cid": cid, "is_typing": is_typing}}, exclude=websocket)

            elif etype == "pong":
                pass

            elif etype == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({"type": "error", "error": "unknown_event"})

    except WebSocketDisconnect:
        pass
    finally:
        hb.cancel()
        left = await manager.leave_all(websocket)
        await manager.disconnect(websocket)
        for cid in left:
            await manager.broadcast_to_conversation(cid, {"type": "presence.leave", "data": {"cid": cid}}, exclude=websocket)


@router.websocket("/ws/conversations/{conversation_id}")
async def ws_conversation_endpoint(websocket: WebSocket, conversation_id: str):
    await ws_endpoint(websocket)



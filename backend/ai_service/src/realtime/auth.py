from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import WebSocket
from backend.ai_service.src.realtime.settings import get_settings

try:
    import jwt as pyjwt  # type: ignore
except Exception:  # pragma: no cover
    pyjwt = None


def _extract_token(ws: WebSocket) -> Optional[str]:
    auth = ws.headers.get("authorization") or ws.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    token = ws.query_params.get("token")
    return token


async def auth_ws(ws: WebSocket) -> Optional[Dict[str, Any]]:
    settings = get_settings()
    token = _extract_token(ws)
    if not token:
        await ws.send_json({"type": "auth.error", "error": "missing_token"})
        await ws.close(code=4401)
        return None

    allowed = settings.allowed_origins
    if allowed:
        origins = {o.strip() for o in allowed.split(",") if o.strip()}
        origin = ws.headers.get("origin") or ws.headers.get("Origin")
        if origin and origin not in origins:
            await ws.send_json({"type": "auth.error", "error": "forbidden_origin"})
            await ws.close(code=4403)
            return None

    if settings.jwt_secret and pyjwt is not None:
        try:
            claims = pyjwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
            await ws.send_json({"type": "auth.ok", "alg": settings.jwt_alg})
            return claims
        except Exception:
            await ws.send_json({"type": "auth.error", "error": "invalid_token"})
            await ws.close(code=4401)
            return None

    if settings.dev_allow_any_token:
        claims = {"sub": f"dev:{token}", "user_id": f"dev:{token}"}
        await ws.send_json({"type": "auth.ok", "mode": "dev"})
        return claims

    await ws.send_json({"type": "auth.error", "error": "unauthorized"})
    await ws.close(code=4401)
    return None



from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass
class WSSettings:
    enabled: bool = True
    ping_interval_sec: int = int(os.getenv("WS_PING_INTERVAL", "25"))
    ping_miss_allowed: int = int(os.getenv("WS_PING_MISS_ALLOWED", "2"))
    max_msg_per_10s: int = int(os.getenv("WS_MAX_MSG_PER_10S", "20"))
    max_frame_bytes: int = int(os.getenv("WS_MAX_FRAME_BYTES", str(1_000_000)))
    allowed_origins: str | None = os.getenv("WS_ALLOWED_ORIGINS")
    redis_url: str | None = os.getenv("WS_REDIS_URL")
    dev_allow_any_token: bool = os.getenv("WS_DEV_ALLOW_ANY_TOKEN", "true").lower() == "true"
    jwt_alg: str = os.getenv("JWT_ALG", "HS256")
    jwt_secret: str | None = os.getenv("JWT_SECRET")
    from dataclasses import field
    subprotocols: list[str] = field(default_factory=lambda: ["bearer", "v1"])


def get_settings() -> WSSettings:
    return WSSettings()



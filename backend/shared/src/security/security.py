from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any, Dict, Optional

from jose import jwt, JWTError
import os

# === JWT helpers ===
ALGORITHM = "HS256"

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(data: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
    from shared.src.config import settings
    to_encode = data.copy()
    exp_minutes = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = _now_utc() + timedelta(minutes=exp_minutes)
    to_encode.update({"exp": expire})
    secret = settings.JWT_SECRET
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_days: Optional[int] = None) -> str:
    to_encode = data.copy()
    exp_days = expires_days or int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    expire = _now_utc() + timedelta(days=exp_days)
    to_encode.update({"exp": expire, "typ": "refresh"})
    secret = os.getenv("JWT_SECRET", "dev-secret")
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Dict[str, Any]:
    from shared.src.config import settings
    secret = settings.JWT_SECRET
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError("Invalid token") from e


def verify_refresh_token(token: str) -> Dict[str, Any]:
    payload = verify_access_token(token)
    if payload.get("typ") == "refresh":
        return payload
    raise ValueError("Not a refresh token")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

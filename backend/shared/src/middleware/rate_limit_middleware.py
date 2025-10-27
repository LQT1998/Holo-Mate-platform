"""Rate limiting middleware for FastAPI applications."""

from __future__ import annotations

import time
import asyncio
from collections import defaultdict, deque
from typing import Deque

from fastapi import Request, status
from fastapi.responses import JSONResponse

from shared.src.config import settings  # để kiểm tra ENV

# Type alias
RateStore = defaultdict[str, Deque[float]]


class InMemoryRateLimiter:
    """In-memory sliding window rate limiter (async-safe with locks)."""

    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.store: RateStore = defaultdict(lambda: deque(maxlen=limit))
        self.lock = asyncio.Lock()

    async def check(self, key: str) -> bool:
        now = time.time()
        async with self.lock:
            dq = self.store[key]
            # Remove old timestamps
            while dq and now - dq[0] > self.window:
                dq.popleft()
            if len(dq) >= self.limit:
                return False
            dq.append(now)
            return True

    async def remaining(self, key: str) -> int:
        dq = self.store[key]
        return max(0, self.limit - len(dq))


async def rate_limit_middleware(request: Request, call_next):
    """Lightweight async rate limiting middleware (function-style)."""
    # Skip rate limit in development
    if settings.ENV.lower() == "dev":
        return await call_next(request)

    # Skip health/docs/static routes
    if request.url.path.startswith(("/health", "/metrics", "/docs", "/openapi")):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"

    # Shared limiters (per-process)
    if not hasattr(rate_limit_middleware, "_minute_limiter"):
        rate_limit_middleware._minute_limiter = InMemoryRateLimiter(limit=60, window=60)
        rate_limit_middleware._hour_limiter = InMemoryRateLimiter(limit=1000, window=3600)
    minute_limiter: InMemoryRateLimiter = rate_limit_middleware._minute_limiter
    hour_limiter: InMemoryRateLimiter = rate_limit_middleware._hour_limiter

    allowed_minute = await minute_limiter.check(client_ip)
    allowed_hour = await hour_limiter.check(client_ip)

    if not (allowed_minute and allowed_hour):
        retry_after = 60 if not allowed_minute else 3600
        headers = {
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit-Minute": str(minute_limiter.limit),
            "X-RateLimit-Limit-Hour": str(hour_limiter.limit),
            "X-RateLimit-Remaining-Minute": str(await minute_limiter.remaining(client_ip)),
            "X-RateLimit-Remaining-Hour": str(await hour_limiter.remaining(client_ip)),
        }
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please try again later."},
            headers=headers,
        )

    # Continue normally
    response = await call_next(request)
    # Attach rate headers to all responses (optional)
    response.headers["X-RateLimit-Limit-Minute"] = str(minute_limiter.limit)
    response.headers["X-RateLimit-Remaining-Minute"] = str(await minute_limiter.remaining(client_ip))
    return response

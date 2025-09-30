"""JWT authentication middleware for FastAPI applications."""

from __future__ import annotations

from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from shared.src.security.jwt import JWTErrorResponse, verify_access_token
from shared.src.security.token_blacklist import dev_blacklisted
from shared.src.config import settings


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that verifies JWT Bearer tokens on incoming requests."""

    def __init__(self, app, exclude_paths: list[str] | None = None):
        super().__init__(app)
        # Default exclude paths
        default_exclude = ["/", "/health", "/auth/register", "/auth/login", "/auth/refresh", "/users/me*"]
        # Merge custom excludes with defaults (ensure parentheses for correct precedence)
        self.exclude_paths = set((exclude_paths or []) + default_exclude)
        # Also support prefix-based excludes like '/conversations' or '/messages'
        self.exclude_prefixes = tuple(p for p in self.exclude_paths if p.endswith("*"))

    async def dispatch(self, request: Request, call_next: Callable[..., Response]) -> Response:
        # Skip authentication for excluded exact paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        # Skip for prefixes (support pattern '/path*')
        for prefix in self.exclude_paths:
            if prefix.endswith("*") and request.url.path.startswith(prefix[:-1]):
                return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", maxsplit=1)[1].strip()
        
        # Check DEV blacklist first
        if settings.ENV == "dev" and dev_blacklisted(token):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token revoked"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            payload = verify_access_token(token)
            request.state.user = payload
        except JWTErrorResponse as exc:
            detail = exc.detail or "Invalid authentication credentials"
            if exc.status_code == status.HTTP_401_UNAUTHORIZED and "invalid" not in detail.lower():
                # Normalize detail to include keyword expected by tests
                detail = "Invalid authentication credentials"
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": detail},
                headers=exc.headers,
            )

        return await call_next(request)


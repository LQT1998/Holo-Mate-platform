"""JWT authentication middleware for FastAPI applications."""

from __future__ import annotations

from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from shared.src.security.jwt import JWTErrorResponse, verify_access_token


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that verifies JWT Bearer tokens on incoming requests."""

    async def dispatch(self, request: Request, call_next: Callable[..., Response]) -> Response:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing bearer token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", maxsplit=1)[1].strip()
        try:
            payload = verify_access_token(token)
            request.state.user = payload
        except JWTErrorResponse as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=exc.headers,
            )

        return await call_next(request)


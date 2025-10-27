"""JWT authentication middleware for FastAPI applications."""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from shared.src.security.jwt import JWTErrorResponse, verify_access_token
from shared.src.security.token_blacklist import dev_blacklisted
from shared.src.config import settings

logger = logging.getLogger(__name__)

# Type alias cho middleware function style
RequestHandler = Callable[[Request], Awaitable[Response]]


def make_auth_middleware(
    exclude_paths: list[str] | None = None,
    exclude_prefixes: tuple[str, ...] | None = None,
) -> RequestHandler:
    """Factory function to create JWT auth middleware with custom exclusions.

    Args:
        exclude_paths: List of exact paths to exclude from auth (e.g., ["/", "/health"])
        exclude_prefixes: Tuple of path prefixes to exclude (e.g., ("/public",))

    Returns:
        Async middleware function
    """
    # Default excluded paths
    if exclude_paths is None:
        exclude_paths = [
            "/", "/health", "/docs", "/openapi.json", "/redoc",
            "/auth/register", "/auth/login", "/auth/refresh",
        ]

    # Default prefix exclusions
    if exclude_prefixes is None:
        exclude_prefixes = ("/users/me",)

    async def auth_middleware_inner(request: Request, call_next: RequestHandler) -> Response:
        """JWT Authentication middleware (function-style, async-safe).

        Features:
        - Validates Bearer token in Authorization header
        - Supports excluded paths/prefixes
        - Handles token revocation (dev blacklist)
        - Attaches decoded user payload to request.state.user
        """
        # --- 1. Skip excluded routes ---
        path = request.url.path
        if path in exclude_paths or any(path.startswith(p) for p in exclude_prefixes):
            return await call_next(request)

        # --- 2. Check Authorization header ---
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", maxsplit=1)[1].strip()

        # --- 3. DEV blacklist (simulate logout) ---
        if settings.ENV.lower() == "dev" and dev_blacklisted(token):
            logger.warning(f"Rejected blacklisted token (dev mode) from {request.client.host}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token revoked"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # --- 4. Verify JWT token ---
        try:
            payload = verify_access_token(token)
            request.state.user = payload  # attach user to request context
        except JWTErrorResponse as exc:
            detail = exc.detail or "Invalid authentication credentials"
            # Normalize message for test expectations
            if exc.status_code == status.HTTP_401_UNAUTHORIZED and "invalid" not in detail.lower():
                detail = "Invalid authentication credentials"

            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": detail},
                headers=exc.headers,
            )
        except Exception as e:
            logger.exception(f"JWT verification failed: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authentication credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # --- 5. Continue if valid ---
        return await call_next(request)

    return auth_middleware_inner


async def auth_middleware(request: Request, call_next: RequestHandler) -> Response:
    """JWT Authentication middleware (function-style, async-safe) with default exclusions.

    Features:
    - Validates Bearer token in Authorization header
    - Supports excluded paths/prefixes
    - Handles token revocation (dev blacklist)
    - Attaches decoded user payload to request.state.user
    """

    # --- 1. Define excluded paths ---
    exclude_paths: list[str] = [
        "/", "/health", "/docs", "/openapi.json", "/redoc",
        "/auth/register", "/auth/login", "/auth/refresh",
    ]
    # Prefix-based exclusions (wildcard-style, e.g. '/users/me*')
    exclude_prefixes: tuple[str, ...] = ("/users/me",)

    # --- 2. Skip excluded routes ---
    path = request.url.path
    if path in exclude_paths or any(path.startswith(p) for p in exclude_prefixes):
        return await call_next(request)

    # --- 3. Check Authorization header ---
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ", maxsplit=1)[1].strip()

    # --- 4. DEV blacklist (simulate logout) ---
    if settings.ENV.lower() == "dev" and dev_blacklisted(token):
        logger.warning(f"Rejected blacklisted token (dev mode) from {request.client.host}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token revoked"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- 5. Verify JWT token ---
    try:
        payload = verify_access_token(token)
        request.state.user = payload  # attach user to request context
    except JWTErrorResponse as exc:
        detail = exc.detail or "Invalid authentication credentials"
        # Normalize message for test expectations
        if exc.status_code == status.HTTP_401_UNAUTHORIZED and "invalid" not in detail.lower():
            detail = "Invalid authentication credentials"

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": detail},
            headers=exc.headers,
        )
    except Exception as e:
        logger.exception(f"JWT verification failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid authentication credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- 6. Continue if valid ---
    return await call_next(request)

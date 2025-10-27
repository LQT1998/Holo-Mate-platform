"""Security headers middleware for FastAPI applications (optimized)."""

from __future__ import annotations
from fastapi import Request, Response
from shared.src.config import settings


async def security_headers_middleware(request: Request, call_next):
    """Add secure HTTP headers to all responses.

    Includes:
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    - Strict-Transport-Security (only in HTTPS/production)
    - Content-Security-Policy (optional, can be tuned per app)
    """
    response: Response = await call_next(request)

    # Baseline security headers (always on)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )

    # Only for production / HTTPS
    if settings.ENV.lower() == "prod":
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )

    # Optional: add CSP in production for web endpoints
    # (relax if you have SPA/frontend serving separately)
    if settings.ENV.lower() == "prod":
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none';",
        )

    return response

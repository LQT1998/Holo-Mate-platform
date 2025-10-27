"""Unified middleware stack for FastAPI applications (Phase 4+)."""

from fastapi import FastAPI
from shared.src.config import settings

# Import all middlewares (đã refactor dạng function-style)
from shared.src.middleware.error_middleware import error_handling_middleware
from shared.src.middleware.logging_middleware import request_logging_middleware
from shared.src.middleware.rate_limit_middleware import rate_limit_middleware
from shared.src.middleware.security_middleware import security_headers_middleware
from shared.src.middleware.cors_middleware import setup_cors_middleware
from shared.src.middleware.auth_middleware import auth_middleware, make_auth_middleware

__all__ = [
    "error_handling_middleware",
    "request_logging_middleware",
    "rate_limit_middleware",
    "security_headers_middleware",
    "setup_cors_middleware",
    "auth_middleware",
    "make_auth_middleware",
    "init_middleware_stack",
]


def init_middleware_stack(app: FastAPI) -> None:
    """Attach all global middlewares to the FastAPI app.

    Order of execution (top → bottom):
    1️⃣ Error handling (catch-all)
    2️⃣ Rate limiting (throttling)
    3️⃣ Request logging (timing + tracing)
    4️⃣ Security headers (hardening)
    5️⃣ CORS (cross-origin policy)
    6️⃣ Auth (optional global auth check)

    Each middleware is environment-aware:
    - In DEV: Logging & error detail verbose
    - In PROD: Secure headers + rate limit active
    """

    # 🧱 1. Error handling (must come first)
    app.middleware("http")(error_handling_middleware)

    # 🚦 2. Rate limiting (skip in dev)
    if settings.ENV.lower() == "prod":
        app.middleware("http")(rate_limit_middleware)

    # 📜 3. Request logging
    app.middleware("http")(request_logging_middleware)

    # 🔒 4. Security headers
    app.middleware("http")(security_headers_middleware)

    # 🌐 5. CORS
    setup_cors_middleware(app)

    # 🔑 6. AUTH middleware is NOT added here - each service must add it explicitly
    #    with service-specific exclusions using make_auth_middleware()

    # ✅ Ready
    print(f"[Middleware] Stack initialized ({settings.ENV.upper()} mode)")

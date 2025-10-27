"""
Holo-Mate Auth Service
Authentication and user management service
"""

from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
import uvicorn

# Routers
from auth_service.src.api import auth, subscriptions, users

# Shared dependencies
from shared.src.db.session import close_engine, create_engine
from shared.src.utils.redis import close_redis, get_redis

# Middleware stack
from shared.src.middleware import init_middleware_stack
from shared.src.middleware.auth_middleware import make_auth_middleware  # ✅ dùng factory mới


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle context for DB and Redis connections."""
    create_engine()
    await get_redis()
    try:
        yield
    finally:
        await close_engine()
        await close_redis()


def create_app() -> FastAPI:
    """Create and configure FastAPI app instance."""
    app = FastAPI(
        title="Holo-Mate Auth Service",
        description="Authentication and user management for Holo-Mate platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ✅ 1. Initialize core middleware stack (CORS, logging, error, security, rate-limit)
    init_middleware_stack(app)

    # ✅ 2. Add JWT authentication middleware (function-style with excludes)
    # Public routes that don't require authentication:
    app.middleware("http")(
        make_auth_middleware(
            exclude_paths=[
                # Root & health
                "/", "/health",
                # Auth endpoints (public)
                "/auth/register", "/auth/login", "/auth/refresh",
                # Documentation (public in DEV)
                "/docs", "/openapi.json", "/redoc", "/favicon.ico",
            ]
        )
    )

    # ✅ 3. Include routers
    app.include_router(auth.router, prefix="/auth")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(subscriptions.router, prefix="/api/v1")

    # ✅ 4. Helper routes
    @app.get("/auth/profile")
    async def protected_check(request: Request):
        """Return current user from JWT (for debug/dev)."""
        return {"user": getattr(request.state, "user", None)}

    @app.get("/")
    async def root():
        """Root health endpoint."""
        return {"message": "Holo-Mate Auth Service", "status": "running"}

    @app.get("/health")
    async def health_check():
        """Basic health check."""
        return {"status": "healthy", "service": "auth_service"}

    return app


# ✅ 5. Application entry point
app = create_app()

if __name__ == "__main__":
    uvicorn.run("auth_service.main:app", host="0.0.0.0", port=8000, reload=True)

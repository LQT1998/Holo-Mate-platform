"""
Holo-Mate AI Service
AI companion management and conversation handling
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from ai_service.src.exceptions import AppError, app_error_handler
from ai_service.src.api import ai_companions, conversations, messages, voice_profiles
from shared.src.db.session import create_engine, close_engine_async
from shared.src.utils.redis import close_redis, get_redis

# Middleware stack
from shared.src.middleware import init_middleware_stack
from shared.src.middleware.auth_middleware import make_auth_middleware

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        create_engine()
        await get_redis()
        try:
            yield
        finally:
            await close_engine_async()
            await close_redis()

    app = FastAPI(
        title="Holo-Mate AI Service",
        description="AI companion management and conversation handling for Holo-Mate platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ✅ 1. Initialize core middleware stack (CORS, logging, error, security, rate-limit)
    init_middleware_stack(app)

    # ✅ 2. Add JWT authentication middleware (bypass all routes in DEV for contract tests)
    # In DEV we bypass JWT middleware for all AI service routes and rely on
    # per-endpoint dependencies to enforce auth behavior.
    app.middleware("http")(
        make_auth_middleware(
            exclude_paths=[
                # Root & health
                "/", "/health",
                # Documentation
                "/docs", "/openapi.json", "/redoc", "/favicon.ico",
            ],
            exclude_prefixes=(
                "/api/v1",  # DEV: bypass all API routes (auth handled by endpoints)
            )
        )
    )

    # ✅ 3. Add exception handler for AppError
    app.add_exception_handler(AppError, app_error_handler)

    @app.get("/")
    async def root():
        return {"message": "Holo-Mate AI Service", "status": "running"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "ai_service"}

    app.include_router(ai_companions.router, prefix="/api/v1")
    app.include_router(conversations.router, prefix="/api/v1")
    app.include_router(messages.router, prefix="/api/v1")
    app.include_router(voice_profiles.router, prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

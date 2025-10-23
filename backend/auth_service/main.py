"""
Holo-Mate Auth Service
Authentication and user management service
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Assuming your API routers are in app.api
from auth_service.src.api import auth, subscriptions, users
from shared.src.db.session import close_engine, create_engine
from shared.src.middleware.auth_middleware import JWTAuthMiddleware
from shared.src.utils.redis import close_redis, get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_engine()
    await get_redis()
    try:
        yield
    finally:
        await close_engine()
        await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Holo-Mate Auth Service",
        description="Authentication and user management for Holo-Mate platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(JWTAuthMiddleware, exclude_paths=["/subscriptions", "/auth/register", "/auth/login", "/auth/refresh", "/docs", "/openapi.json", "/redoc"])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/auth")
    app.include_router(users.router, prefix="/api/v1/users")
    app.include_router(subscriptions.router, prefix="/api/v1")

    @app.get("/auth/profile")
    async def protected_check(request: Request):  # pragma: no cover - simple helper route
        return {"user": getattr(request.state, "user", None)}

    @app.get("/")
    async def root():  # pragma: no cover - simple helper route
        return {"message": "Holo-Mate Auth Service", "status": "running"}

    @app.get("/health")
    async def health_check():  # pragma: no cover - simple helper route
        return {"status": "healthy", "service": "auth_service"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
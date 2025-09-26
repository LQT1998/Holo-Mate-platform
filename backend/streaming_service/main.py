"""
Holo-Mate Streaming Service
Real-time voice processing and WebSocket handling
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.streaming_service.src.api import streaming, devices
from shared.src.db.session import create_engine, close_engine_async
from shared.src.utils.redis import close_redis, get_redis
from shared.src.middleware.auth_middleware import JWTAuthMiddleware

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
        title="Holo-Mate Streaming Service",
        description="Handles device streaming sessions for the Holo-Mate platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(JWTAuthMiddleware, exclude_paths=["/streaming/sessions"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "Holo-Mate Streaming Service", "status": "running"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "streaming_service"}

    app.include_router(streaming.router, prefix="/streaming")
    app.include_router(devices.router)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

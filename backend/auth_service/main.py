"""
Holo-Mate Auth Service
Authentication and user management service
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Assuming your API routers are in app.api
from auth_service.src.api import auth, users, subscriptions
from auth_service.src.config import settings
from shared.src.db.session import close_engine, create_engine
from shared.src.utils.redis import close_redis, get_redis
from shared.src.middleware.auth_middleware import JWTAuthMiddleware

def create_app() -> FastAPI:
    app = FastAPI(
        title="Holo-Mate Auth Service",
        description="Authentication and user management for Holo-Mate platform",
        version="1.0.0",
    )

    app.add_middleware(JWTAuthMiddleware)


    @app.on_event("startup")
    async def on_startup() -> None:
        create_engine()
        await get_redis()


    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        await close_redis()
        await close_engine()

# CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
    app.include_router(auth.router, prefix="/auth")
    app.include_router(users.router)
    app.include_router(subscriptions.router)


    @app.get("/auth/profile")
    async def protected_check(request: Request):
        return {"user": getattr(request.state, "user", None)}

    @app.get("/")
    async def root():
        return {"message": "Holo-Mate Auth Service", "status": "running"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "auth_service"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
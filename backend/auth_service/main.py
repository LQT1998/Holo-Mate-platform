"""
Holo-Mate Auth Service
Authentication and user management service
"""

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Assuming your API routers are in app.api
from auth_service.src.api import auth, users, subscriptions
from auth_service.src.config import settings
from auth_service.src.db.session import get_db
from shared.src.models.base import Base
from shared.src.models import user as user_model
from auth_service.src.services.user_service import UserService

app = FastAPI(
    title="Holo-Mate Auth Service",
    description="Authentication and user management for Holo-Mate platform",
    version="1.0.0"
)

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

@app.get("/")
async def root():
    return {"message": "Holo-Mate Auth Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth_service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
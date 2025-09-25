"""Shared test fixtures for the Holo-Mate platform."""

import os
import sys
from typing import AsyncGenerator, Generator

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Set default environment variables for tests
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture
def auth_base_url() -> str:
    """Base URL for auth service."""
    return "http://localhost:8001"


@pytest.fixture
def ai_base_url() -> str:
    """Base URL for AI service."""
    return "http://localhost:8002"


@pytest.fixture
def streaming_base_url() -> str:
    """Base URL for streaming service."""
    return "http://localhost:8003"


@pytest.fixture
async def client(auth_base_url: str) -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client for making API requests to auth service."""
    async with httpx.AsyncClient(base_url=auth_base_url, timeout=10.0) as client:
        yield client


@pytest.fixture
async def ai_client(ai_base_url: str) -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client for making API requests to AI service."""
    async with httpx.AsyncClient(base_url=ai_base_url, timeout=10.0) as client:
        yield client


@pytest.fixture
async def streaming_client(streaming_base_url: str) -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client for making API requests to streaming service."""
    async with httpx.AsyncClient(base_url=streaming_base_url, timeout=10.0) as client:
        yield client


@pytest.fixture
def db_session() -> Generator[sessionmaker, None, None]:
    """Database session for testing."""
    from backend.shared.src.models.base import Base
    
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def authenticated_user_headers():
    """Fixture providing authenticated user headers for testing"""
    return {
        "Authorization": "Bearer valid_access_token_here",
        "Content-Type": "application/json"
    }

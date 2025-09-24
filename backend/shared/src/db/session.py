"""Async database session utilities shared across services."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import AsyncGenerator as TypingAsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from shared.src.config import settings

DATABASE_URL = str(settings.DATABASE_URL)

# Global engine and session factory
engine = None
SessionLocal = None


def create_engine():
    """Create database engine if not already created."""
    global engine, SessionLocal
    if engine is None:
        engine = create_async_engine(
            DATABASE_URL, 
            echo=settings.DB_ECHO, 
            future=True,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections every hour
        )
        SessionLocal = async_sessionmaker(
            bind=engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    return engine, SessionLocal


async def close_engine():
    """Close database engine and cleanup connections."""
    global engine, SessionLocal
    if engine is not None:
        await engine.dispose()
        engine = None
        SessionLocal = None


@asynccontextmanager
async def lifespan_manager(app):
    """Lifespan manager for FastAPI applications."""
    # Startup
    create_engine()
    yield
    # Shutdown
    await close_engine()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for FastAPI dependencies."""
    if SessionLocal is None:
        create_engine()
    
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Convenience function for manual engine management
async def get_engine():
    """Get or create database engine."""
    if engine is None:
        create_engine()
    return engine

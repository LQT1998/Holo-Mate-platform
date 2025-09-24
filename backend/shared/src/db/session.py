"""Async database session utilities shared across services."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

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
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        SessionLocal = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
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
async def lifespan_manager(app):  # pylint: disable=unused-argument
    """Lifespan manager handling database resources."""

    create_engine()
    try:
        yield
    finally:
        await close_engine()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for FastAPI dependencies."""
    if SessionLocal is None:
        create_engine()

    async with SessionLocal() as session:
        try:
            yield session
        except Exception:  # pragma: no cover - error propagation
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_engine():
    """Get or create database engine."""
    if engine is None:
        create_engine()
    return engine


async def close_engine_async():
    """Compatibility wrapper for closing engine in async contexts."""

    await close_engine()

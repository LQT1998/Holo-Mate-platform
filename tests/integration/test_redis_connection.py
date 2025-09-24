"""Integration tests for Redis connectivity and caching helpers."""

import asyncio
import os
import sys
from typing import AsyncGenerator

import pytest
import pytest_asyncio

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

REDIS_URL = os.getenv("REDIS_URL")
DATABASE_URL = os.getenv("DATABASE_URL")

if not REDIS_URL or not DATABASE_URL:
    pytest.skip(
        "Redis integration tests require DATABASE_URL and REDIS_URL",
        allow_module_level=True,
    )

from backend.shared.src.config import settings
from backend.shared.src.utils.redis import cache_get, cache_set, close_redis, get_redis


def configure_env() -> None:
    os.environ.setdefault("DATABASE_URL", str(settings.DATABASE_URL))
    os.environ.setdefault("REDIS_URL", str(settings.REDIS_URL))


@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator:
    configure_env()
    await close_redis()
    client = await get_redis()
    try:
        yield client
    finally:
        await close_redis()


@pytest.mark.asyncio
async def test_redis_ping(redis_client) -> None:  # type: ignore[no-untyped-def]
    pong = await redis_client.ping()
    assert pong is True


@pytest.mark.asyncio
async def test_cache_set_and_get(redis_client) -> None:  # type: ignore[no-untyped-def]
    key = "test:redis:cache"
    value = "cached-value"

    await cache_set(key, value, expire=5)
    cached = await cache_get(key)
    if isinstance(cached, bytes):  # Safety for non-decoded responses
        cached = cached.decode()

    assert cached == value


@pytest.mark.asyncio
async def test_cache_expiration(redis_client) -> None:  # type: ignore[no-untyped-def]
    key = "test:redis:expire"
    value = "expiring-value"

    await cache_set(key, value, expire=1)
    await asyncio.sleep(2)

    cached = await cache_get(key)
    assert cached is None


@pytest.mark.asyncio
async def test_cleanup(redis_client) -> None:  # type: ignore[no-untyped-def]
    original = redis_client
    await close_redis()
    new_client = await get_redis()
    try:
        assert new_client is not original
    finally:
        await close_redis()


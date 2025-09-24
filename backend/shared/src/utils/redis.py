"""Asynchronous Redis utilities shared across backend services."""

from __future__ import annotations

import logging
from typing import Optional

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError

from shared.src.config import settings

LOGGER = logging.getLogger(__name__)

_redis_client: Optional[Redis] = None
_redis_pool: Optional[ConnectionPool] = None


async def get_redis() -> Redis:
    """Return the singleton asynchronous Redis client.

    Returns:
        Redis: Active async Redis client.

    Raises:
        RedisError: If the client fails to initialize.
    """

    global _redis_client, _redis_pool

    if _redis_client is not None:
        return _redis_client

    try:
        _redis_pool = ConnectionPool.from_url(str(settings.REDIS_URL))
        _redis_client = Redis(connection_pool=_redis_pool, decode_responses=True)
        await _redis_client.ping()
        return _redis_client
    except RedisError as error:  # pragma: no cover - logging path
        LOGGER.exception("Failed to initialize Redis client")
        raise


async def close_redis() -> None:
    """Close Redis client and release the connection pool."""

    global _redis_client, _redis_pool

    if _redis_client is not None:
        try:
            if hasattr(_redis_client, "aclose"):
                await _redis_client.aclose()
            else:  # pragma: no cover - fallback for older redis versions
                await _redis_client.close()
        except (RuntimeError, RedisError) as error:  # pragma: no cover - best effort cleanup
            LOGGER.warning("Error closing Redis client", exc_info=error)
        finally:
            _redis_client = None

    if _redis_pool is not None:
        try:
            await _redis_pool.disconnect()
        except (RuntimeError, RedisError) as error:  # pragma: no cover - best effort cleanup
            LOGGER.warning("Error disconnecting Redis pool", exc_info=error)
        finally:
            _redis_pool = None


async def cache_set(key: str, value: str, expire: int = 60) -> None:
    """Store a value in Redis cache with expiration.

    Args:
        key: Cache key.
        value: Value to store.
        expire: Expiration time in seconds (default 60).
    """

    client = await get_redis()
    await client.set(name=key, value=value, ex=expire)


async def cache_get(key: str) -> Optional[str]:
    """Retrieve a value from Redis cache.

    Args:
        key: Cache key to retrieve.

    Returns:
        Optional[str]: Cached value if present, otherwise ``None``.
    """

    client = await get_redis()
    return await client.get(name=key)



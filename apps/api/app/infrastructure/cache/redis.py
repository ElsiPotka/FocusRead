from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

import redis.asyncio as redis
from fastapi import Depends
from redis.asyncio import Redis

from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.config.settings import settings
from app.infrastructure.logging.logger import log

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class RedisManager:
    def __init__(self) -> None:
        self._client: Redis | None = None

    def init(self, redis_url: str) -> None:
        if self._client is not None:
            return

        self._client = redis.from_url(
            redis_url,
            decode_responses=False,
            socket_timeout=5,
            socket_connect_timeout=5,
            health_check_interval=30,
        )

    async def close(self) -> None:
        if self._client is None:
            return

        await self._client.aclose()
        self._client = None

    @property
    def client(self) -> Redis | None:
        return self._client

    @property
    def is_initialized(self) -> bool:
        return self._client is not None


redis_manager = RedisManager()


async def init_redis(*, check_connection: bool) -> None:
    redis_manager.init(settings.REDIS_URL)

    if not check_connection:
        log.info("Redis client initialized without eager connection check.")
        return

    if redis_manager.client is None:
        raise RuntimeError("Redis client was not initialized.")

    await redis_manager.client.ping()
    log.info("Redis initialized and connection verified.")


async def close_redis() -> None:
    await redis_manager.close()
    log.info("Redis client closed.")


async def get_redis() -> AsyncIterator[Redis]:
    if not redis_manager.is_initialized:
        await init_redis(check_connection=False)

    if redis_manager.client is None:
        raise RuntimeError("Redis manager is not initialized.")

    yield redis_manager.client


RedisClient = Annotated[Redis, Depends(get_redis)]


async def get_cache() -> AsyncIterator[RedisCache]:
    if not redis_manager.is_initialized:
        await init_redis(check_connection=False)

    if redis_manager.client is None:
        raise RuntimeError("Redis manager is not initialized.")

    yield RedisCache(redis_manager.client)


async def check_redis_health() -> bool:
    if not redis_manager.is_initialized or redis_manager.client is None:
        return False

    try:
        await redis_manager.client.ping()
    except Exception:
        return False

    return True

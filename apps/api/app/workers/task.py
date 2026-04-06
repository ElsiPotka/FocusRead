from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from celery.utils.log import get_task_logger

from app.infrastructure.cache.keys import build_cache_key
from app.infrastructure.cache.redis import redis_manager
from app.infrastructure.config.settings import settings
from app.infrastructure.persistence.db import sessionmanager
from app.workers.broker import celery_app

logger = get_task_logger(__name__)


def _ensure_worker_infra_initialized() -> None:
    if not sessionmanager.is_initialized:
        sessionmanager.init(settings.SQLALCHEMY_DATABASE_URI)
    if not redis_manager.is_initialized:
        redis_manager.init(settings.REDIS_URL)


@celery_app.task(name="app.workers.task.ping")
def ping_task() -> dict[str, str]:
    logger.info("Running Celery ping task")
    return {"status": "ok", "worker": "focusread"}


async def _ping_redis() -> dict[str, str]:
    _ensure_worker_infra_initialized()

    if redis_manager.client is None:
        raise RuntimeError("Redis client is not initialized in worker process.")

    await redis_manager.client.ping()
    heartbeat_key = build_cache_key("celery", "heartbeat")
    heartbeat_value = datetime.now(UTC).isoformat().encode("utf-8")
    await redis_manager.client.set(
        heartbeat_key,
        heartbeat_value,
        ex=settings.CACHE_DEFAULT_TTL_SECONDS,
    )

    return {"status": "ok", "redis": "reachable", "heartbeat_key": heartbeat_key}


@celery_app.task(name="app.workers.task.ping_redis")
def ping_redis_task() -> dict[str, str]:
    logger.info("Running Redis ping task")
    return asyncio.run(_ping_redis())

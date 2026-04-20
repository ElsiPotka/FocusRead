from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from uuid import UUID

from celery.utils.log import get_task_logger

from app.infrastructure.cache.keys import (
    book_asset_chunk_key,
    book_asset_processing_channel,
    build_cache_key,
)
from app.infrastructure.cache.redis import redis_manager
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.config.settings import settings
from app.infrastructure.persistence.db import sessionmanager
from app.workers.broker import celery_app

logger = get_task_logger(__name__)

CHUNK_CACHE_TTL_SECONDS = 1800  # 30 minutes


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


async def _publish_asset_progress(
    asset_id: str,
    *,
    status: str,
    progress: int,
    chunks_ready: int,
    total_chunks: int | None = None,
    error: str | None = None,
) -> None:
    client = redis_manager.client
    if client is None:
        return

    channel = book_asset_processing_channel(asset_id)
    event: dict[str, object] = {
        "status": status,
        "progress": progress,
        "chunks_ready": chunks_ready,
        "total_chunks": total_chunks,
    }
    if error:
        event["error"] = error
    await client.publish(channel, json.dumps(event))


async def _process_book_asset(asset_id: str) -> dict[str, str]:
    from app.domain.book_asset.value_objects import (
        BookAssetId,
        PageCount,
        ProcessingError,
        ProcessingStatus,
        TotalChunks,
        WordCount,
    )
    from app.domain.book_chunks.entities import BookChunk
    from app.domain.book_chunks.value_objects import (
        ChunkIndex,
        ChunkWordCount,
        ChunkWordData,
        StartWordIndex,
    )
    from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
    from app.infrastructure.storage.file_storage import get_file_storage
    from app.workers.pdf_processor import PDFProcessor

    _ensure_worker_infra_initialized()

    cache = RedisCache(redis_manager.client) if redis_manager.client else None
    file_storage = get_file_storage()

    try:
        typed_asset_id = BookAssetId(UUID(asset_id))
    except ValueError:
        logger.error("Invalid asset id %s", asset_id)
        return {"status": "error", "reason": "invalid_asset_id"}

    async with sessionmanager.session() as session:
        uow = SqlAlchemyUnitOfWork(session)

        asset = await uow.book_assets.get(typed_asset_id)
        if asset is None:
            logger.error("Asset %s not found", asset_id)
            return {"status": "error", "reason": "asset_not_found"}

        if asset.processing_status is ProcessingStatus.READY:
            logger.info("Asset %s already ready — skipping", asset_id)
            chunks_done = asset.total_chunks.value if asset.total_chunks else 0
            await _publish_asset_progress(
                asset_id,
                status="ready",
                progress=100,
                chunks_ready=chunks_done,
                total_chunks=chunks_done,
            )
            return {
                "status": "ready",
                "asset_id": asset_id,
                "chunks": str(chunks_done),
            }

        try:
            asset.mark_processing()
            await uow.book_assets.save(asset)
            await uow.commit()
        except Exception:
            logger.exception("Failed to mark asset %s as processing", asset_id)
            raise

        storage_path = file_storage.resolve_path(
            storage_key=asset.storage_key.value,
        )

        try:
            with PDFProcessor(storage_path) as processor:
                page_count = processor.page_count
                asset.update_processing_details(page_count=PageCount(page_count))
                await uow.book_assets.save(asset)
                await uow.commit()

                running_word_count = 0
                chunk_count = 0
                any_images = False

                for raw_chunk in processor.extract_chunks():
                    chunk_entity = BookChunk.create(
                        book_asset_id=asset.id,
                        chunk_index=ChunkIndex(chunk_count),
                        start_word_index=StartWordIndex(running_word_count),
                        word_data=ChunkWordData(raw_chunk.tokens),
                        word_count=ChunkWordCount(raw_chunk.word_count),
                        page_start=raw_chunk.page_start,
                        page_end=raw_chunk.page_end,
                    )
                    await uow.book_chunks.upsert_by_asset_index(chunk_entity)
                    await uow.commit()

                    if cache is not None:
                        await cache.set_json(
                            book_asset_chunk_key(asset_id, chunk_count),
                            raw_chunk.tokens,
                            compress=True,
                            ttl_seconds=CHUNK_CACHE_TTL_SECONDS,
                        )

                    running_word_count += raw_chunk.word_count
                    if raw_chunk.has_images:
                        any_images = True
                    chunk_count += 1

                    if page_count > 0:
                        progress = min(int((raw_chunk.page_end / page_count) * 100), 99)
                    else:
                        progress = 0

                    await _publish_asset_progress(
                        asset_id,
                        status="processing",
                        progress=progress,
                        chunks_ready=chunk_count,
                    )

                    logger.info(
                        "Asset %s: chunk %d ready (%d words)",
                        asset_id,
                        chunk_count - 1,
                        raw_chunk.word_count,
                    )

                any_images = any_images or processor.has_images

            asset.update_processing_details(
                word_count=WordCount(running_word_count),
                total_chunks=TotalChunks(chunk_count),
                has_images=any_images,
                toc_extracted=False,
            )
            asset.mark_ready()
            await uow.book_assets.save(asset)
            await uow.commit()

            await _publish_asset_progress(
                asset_id,
                status="ready",
                progress=100,
                chunks_ready=chunk_count,
                total_chunks=chunk_count,
            )

            logger.info(
                "Asset %s processing complete: %d chunks, %d words",
                asset_id,
                chunk_count,
                running_word_count,
            )
            return {
                "status": "ready",
                "asset_id": asset_id,
                "chunks": str(chunk_count),
                "words": str(running_word_count),
            }

        except Exception as exc:
            logger.exception("Asset %s processing failed", asset_id)

            error_msg = str(exc)[:5000]
            asset.mark_error(ProcessingError(error_msg) if error_msg.strip() else None)
            await uow.book_assets.save(asset)
            await uow.commit()

            await _publish_asset_progress(
                asset_id,
                status="error",
                progress=0,
                chunks_ready=0,
                error=error_msg,
            )
            raise


@celery_app.task(
    name="app.workers.task.process_book_asset",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def process_book_asset_task(self, asset_id: str) -> dict[str, str]:
    logger.info("Starting PDF processing for asset %s", asset_id)
    try:
        return asyncio.run(_process_book_asset(asset_id))
    except Exception as exc:
        logger.exception("Process book-asset task failed for %s", asset_id)
        raise self.retry(exc=exc) from exc

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from uuid import UUID

from celery.utils.log import get_task_logger

from app.infrastructure.cache.keys import (
    book_chunk_key,
    book_processing_channel,
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


async def _publish_progress(
    book_id: str,
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

    channel = book_processing_channel(book_id)
    event = {
        "status": status,
        "progress": progress,
        "chunks_ready": chunks_ready,
        "total_chunks": total_chunks,
    }
    if error:
        event["error"] = error
    await client.publish(channel, json.dumps(event))


async def _process_book(book_id: str) -> dict[str, str]:
    from app.domain.book_chunks.entities import BookChunk
    from app.domain.book_chunks.value_objects import (
        ChunkIndex,
        ChunkWordCount,
        ChunkWordData,
        StartWordIndex,
    )
    from app.domain.books.value_objects import (
        BookId,
        BookPageCount,
        BookProcessingError,
        BookTotalChunks,
        BookWordCount,
    )
    from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
    from app.workers.pdf_processor import PDFProcessor

    _ensure_worker_infra_initialized()

    cache = RedisCache(redis_manager.client) if redis_manager.client else None

    try:
        typed_book_id = BookId(UUID(book_id))
    except ValueError:
        logger.error("Invalid book id %s", book_id)
        return {"status": "error", "reason": "invalid_book_id"}

    async with sessionmanager.session() as session:
        uow = SqlAlchemyUnitOfWork(session)

        book = await uow.books.get(typed_book_id)
        if book is None:
            logger.error("Book %s not found", book_id)
            return {"status": "error", "reason": "book_not_found"}

        try:
            book.mark_processing()
            await uow.books.save(book)
            await uow.commit()
        except Exception:
            logger.exception("Failed to mark book %s as processing", book_id)
            raise

        try:
            with PDFProcessor(book.file_path.value) as processor:
                page_count = processor.page_count
                book.update_metadata(page_count=BookPageCount(page_count))
                await uow.books.save(book)
                await uow.commit()

                estimated_chunks: int | None = None

                running_word_count = 0
                chunk_count = 0
                any_images = False

                for raw_chunk in processor.extract_chunks():
                    chunk_entity = BookChunk.create(
                        book_id=book.id,
                        chunk_index=ChunkIndex(chunk_count),
                        start_word_index=StartWordIndex(running_word_count),
                        word_data=ChunkWordData(raw_chunk.tokens),
                        word_count=ChunkWordCount(raw_chunk.word_count),
                        page_start=raw_chunk.page_start,
                        page_end=raw_chunk.page_end,
                    )

                    await uow.book_chunks.save(chunk_entity)
                    await uow.commit()

                    if cache is not None:
                        await cache.set_json(
                            book_chunk_key(book_id, chunk_count),
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

                    await _publish_progress(
                        book_id,
                        status="processing",
                        progress=progress,
                        chunks_ready=chunk_count,
                        total_chunks=estimated_chunks,
                    )

                    logger.info(
                        "Book %s: chunk %d ready (%d words)",
                        book_id,
                        chunk_count - 1,
                        raw_chunk.word_count,
                    )

                any_images = any_images or processor.has_images

            book.update_processing_details(
                word_count=BookWordCount(running_word_count),
                total_chunks=BookTotalChunks(chunk_count),
                has_images=any_images,
                toc_extracted=False,
            )
            book.mark_ready()
            await uow.books.save(book)
            await uow.commit()

            await _publish_progress(
                book_id,
                status="ready",
                progress=100,
                chunks_ready=chunk_count,
                total_chunks=chunk_count,
            )

            logger.info(
                "Book %s processing complete: %d chunks, %d words",
                book_id,
                chunk_count,
                running_word_count,
            )
            return {
                "status": "ready",
                "book_id": book_id,
                "chunks": str(chunk_count),
                "words": str(running_word_count),
            }

        except Exception as exc:
            logger.exception("Book %s processing failed", book_id)

            error_msg = str(exc)[:5000]
            book.mark_error(
                BookProcessingError(error_msg) if error_msg.strip() else None
            )
            await uow.books.save(book)
            await uow.commit()

            await _publish_progress(
                book_id,
                status="error",
                progress=0,
                chunks_ready=0,
                error=error_msg,
            )
            raise


@celery_app.task(
    name="app.workers.task.process_book",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def process_book_task(self, book_id: str) -> dict[str, str]:
    logger.info("Starting PDF processing for book %s", book_id)
    try:
        return asyncio.run(_process_book(book_id))
    except Exception as exc:
        logger.exception("Process book task failed for %s", book_id)
        raise self.retry(exc=exc) from exc

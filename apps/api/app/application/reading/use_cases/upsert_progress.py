from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.reading_sessions.entities import ReadingSession
from app.domain.reading_sessions.value_objects import (
    CurrentChunk,
    CurrentWordIndex,
    WordsPerFlash,
    WpmSpeed,
)
from app.domain.reading_stats.entities import ReadingStat
from app.domain.reading_stats.value_objects import SessionDate
from app.infrastructure.cache.keys import reading_session_key

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.cache.redis_cache import RedisCache

SESSION_CACHE_TTL_SECONDS = 600  # 10 minutes


@dataclass(frozen=True, slots=True)
class ProgressUpdate:
    current_word_index: int
    current_chunk: int
    wpm_speed: int | None = None
    words_per_flash: int | None = None
    words_read_delta: int = 0
    time_spent_delta_sec: int = 0


class UpsertProgress:
    def __init__(self, uow: AbstractUnitOfWork, cache: RedisCache) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(
        self,
        *,
        book_id: UUID,
        user_id: UUID,
        update: ProgressUpdate,
    ) -> ReadingSession:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        session = await self._uow.reading_sessions.get(
            user_id=UserId(user_id),
            book_id=BookId(book_id),
        )
        if session is None:
            session = ReadingSession.create(
                user_id=UserId(user_id),
                book_id=BookId(book_id),
                wpm_speed=WpmSpeed(update.wpm_speed) if update.wpm_speed else None,
                words_per_flash=WordsPerFlash(update.words_per_flash)
                if update.words_per_flash
                else None,
            )

        session.update_progress(
            current_word_index=CurrentWordIndex(update.current_word_index),
            current_chunk=CurrentChunk(update.current_chunk),
            wpm_speed=WpmSpeed(update.wpm_speed) if update.wpm_speed else None,
            words_per_flash=WordsPerFlash(update.words_per_flash)
            if update.words_per_flash
            else None,
        )
        await self._uow.reading_sessions.save(session)

        today = SessionDate(date.today())
        stat = await self._uow.reading_stats.get(
            user_id=UserId(user_id),
            book_id=BookId(book_id),
            session_date=today,
        )
        if stat is None:
            stat = ReadingStat.create(
                user_id=UserId(user_id),
                book_id=BookId(book_id),
                session_date=today,
            )

        if update.words_read_delta > 0 or update.time_spent_delta_sec > 0:
            stat.record_activity(
                words_read_delta=update.words_read_delta,
                time_spent_delta_sec=update.time_spent_delta_sec,
            )
        await self._uow.reading_stats.save(stat)

        await self._uow.commit()

        cache_key = reading_session_key(str(user_id), str(book_id))
        await self._cache.set_json(
            cache_key,
            {
                "current_word_index": session.current_word_index.value,
                "current_chunk": session.current_chunk.value,
                "wpm_speed": session.wpm_speed.value,
                "words_per_flash": session.words_per_flash.value,
            },
            ttl_seconds=SESSION_CACHE_TTL_SECONDS,
        )

        return session

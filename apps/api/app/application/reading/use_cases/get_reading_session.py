from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.infrastructure.cache.keys import reading_session_key

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.reading_sessions.entities import ReadingSession
    from app.infrastructure.cache.redis_cache import RedisCache

SESSION_CACHE_TTL_SECONDS = 600  # 10 minutes


class GetReadingSession:
    def __init__(self, uow: AbstractUnitOfWork, cache: RedisCache) -> None:
        self._uow = uow
        self._cache = cache

    async def execute(
        self,
        *,
        book_id: UUID,
        user_id: UUID,
    ) -> ReadingSession | None:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")
        library_item = await self._uow.library_items.get_active_for_user_book(
            user_id=UserId(user_id),
            book_id=BookId(book_id),
        )
        if library_item is None:
            raise NotFoundError("Library item not found")

        cache_key = reading_session_key(str(user_id), str(book_id))
        cached = await self._cache.get_json(cache_key)
        if cached is not None:
            await self._cache.touch(cache_key, ttl_seconds=SESSION_CACHE_TTL_SECONDS)

        session = await self._uow.reading_sessions.get_for_library_item(
            library_item_id=library_item.id,
        )

        if session is not None and cached is None:
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

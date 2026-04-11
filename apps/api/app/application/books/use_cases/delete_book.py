from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.infrastructure.cache.keys import book_ownership_key

if TYPE_CHECKING:
    from uuid import UUID

    from app.infrastructure.cache.redis_cache import RedisCache


class DeleteBook:
    def __init__(self, uow, cache: RedisCache | None = None) -> None:  # noqa: TC001
        self._uow = uow
        self._cache = cache

    async def execute(self, *, book_id: UUID, owner_user_id: UUID) -> None:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(owner_user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")
        await self._uow.books.delete(book_id=book.id)
        await self._uow.commit()

        if self._cache is not None:
            await self._cache.delete(
                book_ownership_key(str(owner_user_id), str(book_id))
            )

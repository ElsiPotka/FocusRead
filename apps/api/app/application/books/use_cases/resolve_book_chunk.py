from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True, slots=True)
class ResolvedChunk:
    chunk_index: int
    local_offset: int
    start_word_index: int
    word_count: int


class ResolveBookChunk:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        book_id: UUID,
        word_index: int,
        owner_user_id: UUID,
    ) -> ResolvedChunk:
        # 1. Verify book ownership
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(owner_user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        # 2. Find chunk containing this word index
        chunk = await self._uow.book_chunks.get_by_word_index(
            book_asset_id=book.primary_asset_id,
            start_word_index=word_index,
        )
        if chunk is None:
            raise NotFoundError("No chunk found for the given word index")

        # 3. Compute local offset within the chunk
        local_offset = word_index - chunk.start_word_index.value

        return ResolvedChunk(
            chunk_index=chunk.chunk_index.value,
            local_offset=local_offset,
            start_word_index=chunk.start_word_index.value,
            word_count=chunk.word_count.value,
        )

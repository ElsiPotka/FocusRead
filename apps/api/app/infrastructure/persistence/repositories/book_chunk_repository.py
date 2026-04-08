from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, func, select

from app.domain.book_chunks.entities import BookChunk
from app.domain.book_chunks.repositories import BookChunkRepository
from app.domain.book_chunks.value_objects import (
    BookChunkId,
    ChunkIndex,
    ChunkWordCount,
    ChunkWordData,
    StartWordIndex,
)
from app.domain.books.value_objects import BookId
from app.infrastructure.persistence.models.book_chunk import BookChunkModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyBookChunkRepository(BookChunkRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, chunk: BookChunk) -> None:
        model = await self.session.get(BookChunkModel, chunk.id.value)

        if model is None:
            model = BookChunkModel(
                id=chunk.id.value,
                book_id=chunk.book_id.value,
                chunk_index=chunk.chunk_index.value,
                start_word_index=chunk.start_word_index.value,
                word_data=chunk.word_data.value,
                word_count=chunk.word_count.value,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                created_at=chunk.created_at,
                updated_at=chunk.updated_at,
            )
            self.session.add(model)
            return

        model.chunk_index = chunk.chunk_index.value
        model.start_word_index = chunk.start_word_index.value
        model.word_data = chunk.word_data.value
        model.word_count = chunk.word_count.value
        model.page_start = chunk.page_start
        model.page_end = chunk.page_end
        model.updated_at = chunk.updated_at

    async def save_many(self, chunks: list[BookChunk]) -> None:
        for chunk in chunks:
            await self.save(chunk)

    async def get_by_index(
        self, *, book_id: BookId, chunk_index: ChunkIndex
    ) -> BookChunk | None:
        stmt = select(BookChunkModel).where(
            BookChunkModel.book_id == book_id.value,
            BookChunkModel.chunk_index == chunk_index.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_word_index(
        self, *, book_id: BookId, start_word_index: int
    ) -> BookChunk | None:
        stmt = (
            select(BookChunkModel)
            .where(
                BookChunkModel.book_id == book_id.value,
                BookChunkModel.start_word_index <= start_word_index,
            )
            .order_by(BookChunkModel.start_word_index.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def count_for_book(self, *, book_id: BookId) -> int:
        stmt = (
            select(func.count())
            .select_from(BookChunkModel)
            .where(BookChunkModel.book_id == book_id.value)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete_for_book(self, *, book_id: BookId) -> None:
        stmt = delete(BookChunkModel).where(BookChunkModel.book_id == book_id.value)
        await self.session.execute(stmt)

    @staticmethod
    def _to_entity(model: BookChunkModel) -> BookChunk:
        return BookChunk(
            id=BookChunkId(model.id),
            book_id=BookId(model.book_id),
            chunk_index=ChunkIndex(model.chunk_index),
            start_word_index=StartWordIndex(model.start_word_index),
            word_data=ChunkWordData(model.word_data),
            word_count=ChunkWordCount(model.word_count),
            page_start=model.page_start,
            page_end=model.page_end,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

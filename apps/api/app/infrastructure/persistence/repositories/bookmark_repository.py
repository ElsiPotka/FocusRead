from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from app.domain.auth.value_objects import UserId
from app.domain.bookmark.entities import Bookmark
from app.domain.bookmark.repositories import BookmarkRepository
from app.domain.bookmark.value_objects import BookmarkId, BookmarkLabel, BookmarkNote
from app.domain.books.value_objects import BookId  # noqa: TC001
from app.infrastructure.persistence.models.bookmark import BookmarkModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyBookmarkRepository(BookmarkRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, bookmark: Bookmark) -> None:
        model = await self.session.get(BookmarkModel, bookmark.id.value)

        if model is None:
            model = BookmarkModel(
                id=bookmark.id.value,
                user_id=bookmark.user_id.value,
                book_id=bookmark.book_id.value,
                word_index=bookmark.word_index,
                chunk_index=bookmark.chunk_index,
                page_number=bookmark.page_number,
                label=bookmark.label.value if bookmark.label else None,
                note=bookmark.note.value if bookmark.note else None,
                created_at=bookmark.created_at,
                updated_at=bookmark.updated_at,
            )
            self.session.add(model)
            return

        model.word_index = bookmark.word_index
        model.chunk_index = bookmark.chunk_index
        model.page_number = bookmark.page_number
        model.label = bookmark.label.value if bookmark.label else None
        model.note = bookmark.note.value if bookmark.note else None
        model.updated_at = bookmark.updated_at

    async def get(self, bookmark_id: BookmarkId) -> Bookmark | None:
        model = await self.session.get(BookmarkModel, bookmark_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_for_owner(
        self, *, bookmark_id: BookmarkId, user_id: UserId
    ) -> Bookmark | None:
        stmt = select(BookmarkModel).where(
            BookmarkModel.id == bookmark_id.value,
            BookmarkModel.user_id == user_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_book(
        self, *, user_id: UserId, book_id: BookId
    ) -> list[Bookmark]:
        stmt = (
            select(BookmarkModel)
            .where(
                BookmarkModel.user_id == user_id.value,
                BookmarkModel.book_id == book_id.value,
            )
            .order_by(BookmarkModel.created_at)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def delete(self, *, bookmark_id: BookmarkId) -> None:
        stmt = delete(BookmarkModel).where(BookmarkModel.id == bookmark_id.value)
        await self.session.execute(stmt)

    @staticmethod
    def _to_entity(model: BookmarkModel) -> Bookmark:
        return Bookmark(
            id=BookmarkId(model.id),
            user_id=UserId(model.user_id),
            book_id=BookId(model.book_id),
            word_index=model.word_index,
            chunk_index=model.chunk_index,
            page_number=model.page_number,
            label=BookmarkLabel(model.label) if model.label else None,
            note=BookmarkNote(model.note) if model.note else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

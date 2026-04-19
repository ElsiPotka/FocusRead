from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from app.domain.bookmark.entities import Bookmark
from app.domain.bookmark.repositories import BookmarkRepository
from app.domain.bookmark.value_objects import BookmarkId, BookmarkLabel, BookmarkNote
from app.domain.library_item.value_objects import LibraryItemId
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
                library_item_id=bookmark.library_item_id.value,
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

        model.library_item_id = bookmark.library_item_id.value
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

    async def list_for_library_item(
        self, *, library_item_id: LibraryItemId
    ) -> list[Bookmark]:
        stmt = (
            select(BookmarkModel)
            .where(BookmarkModel.library_item_id == library_item_id.value)
            .order_by(BookmarkModel.created_at)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def delete(self, *, bookmark_id: BookmarkId) -> None:
        stmt = delete(BookmarkModel).where(BookmarkModel.id == bookmark_id.value)
        await self.session.execute(stmt)

    @staticmethod
    def _to_entity(model: BookmarkModel) -> Bookmark:
        return Bookmark(
            id=BookmarkId(model.id),
            library_item_id=LibraryItemId(model.library_item_id),
            word_index=model.word_index,
            chunk_index=model.chunk_index,
            page_number=model.page_number,
            label=BookmarkLabel(model.label) if model.label else None,
            note=BookmarkNote(model.note) if model.note else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

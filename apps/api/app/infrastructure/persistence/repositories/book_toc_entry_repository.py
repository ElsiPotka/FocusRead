from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from app.domain.book_asset.value_objects import BookAssetId
from app.domain.book_toc_entry.entities import BookTOCEntry
from app.domain.book_toc_entry.repositories import BookTOCEntryRepository
from app.domain.book_toc_entry.value_objects import BookTOCEntryId, BookTOCTitle
from app.infrastructure.persistence.models.book_toc_entry import BookTOCEntryModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyBookTOCEntryRepository(BookTOCEntryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entry: BookTOCEntry) -> None:
        model = await self.session.get(BookTOCEntryModel, entry.id.value)
        if model is None:
            model = BookTOCEntryModel(
                id=entry.id.value,
                book_asset_id=entry.book_asset_id.value,
                parent_id=entry.parent_id.value if entry.parent_id else None,
                title=entry.title.value,
                level=entry.level,
                order_index=entry.order_index,
                page_start=entry.page_start,
                start_word_index=entry.start_word_index,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
            )
            self.session.add(model)
            return

        model.book_asset_id = entry.book_asset_id.value
        model.parent_id = entry.parent_id.value if entry.parent_id else None
        model.title = entry.title.value
        model.level = entry.level
        model.order_index = entry.order_index
        model.page_start = entry.page_start
        model.start_word_index = entry.start_word_index
        model.updated_at = entry.updated_at

    async def get(self, entry_id: BookTOCEntryId) -> BookTOCEntry | None:
        model = await self.session.get(BookTOCEntryModel, entry_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_asset(self, *, book_asset_id: BookAssetId) -> list[BookTOCEntry]:
        stmt = (
            select(BookTOCEntryModel)
            .where(BookTOCEntryModel.book_asset_id == book_asset_id.value)
            .order_by(BookTOCEntryModel.order_index)
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def save_many(self, entries: list[BookTOCEntry]) -> None:
        for entry in entries:
            await self.save(entry)

    async def delete_for_asset(self, *, book_asset_id: BookAssetId) -> None:
        stmt = delete(BookTOCEntryModel).where(
            BookTOCEntryModel.book_asset_id == book_asset_id.value,
        )
        await self.session.execute(stmt)

    @staticmethod
    def _to_entity(model: BookTOCEntryModel) -> BookTOCEntry:
        return BookTOCEntry(
            id=BookTOCEntryId(model.id),
            book_asset_id=BookAssetId(model.book_asset_id),
            title=BookTOCTitle(model.title),
            level=model.level,
            order_index=model.order_index,
            parent_id=BookTOCEntryId(model.parent_id) if model.parent_id else None,
            page_start=model.page_start,
            start_word_index=model.start_word_index,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

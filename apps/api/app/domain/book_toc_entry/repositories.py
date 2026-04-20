from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.book_asset.value_objects import BookAssetId
    from app.domain.book_toc_entry.entities import BookTOCEntry
    from app.domain.book_toc_entry.value_objects import BookTOCEntryId


class BookTOCEntryRepository(ABC):
    @abstractmethod
    async def save(self, entry: BookTOCEntry) -> None: ...

    @abstractmethod
    async def get(self, entry_id: BookTOCEntryId) -> BookTOCEntry | None: ...

    @abstractmethod
    async def list_for_asset(
        self, *, book_asset_id: BookAssetId
    ) -> list[BookTOCEntry]: ...

    @abstractmethod
    async def save_many(self, entries: list[BookTOCEntry]) -> None: ...

    @abstractmethod
    async def upsert_by_asset_order(self, entry: BookTOCEntry) -> BookTOCEntry:
        """Idempotent upsert keyed on (book_asset_id, order_index).

        If an entry already exists at `(entry.book_asset_id,
        entry.order_index)`, its content is updated in place (reusing the
        existing primary key so partial TOC extraction runs resume
        safely). Otherwise the incoming entry is inserted. Returns the
        persisted entity.
        """

    @abstractmethod
    async def delete_for_asset(self, *, book_asset_id: BookAssetId) -> None: ...

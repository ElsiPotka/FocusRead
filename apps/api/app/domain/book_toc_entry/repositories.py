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
    async def delete_for_asset(self, *, book_asset_id: BookAssetId) -> None: ...

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.book_asset.entities import BookAsset
    from app.domain.book_asset.value_objects import BookAssetId, Sha256
    from app.domain.books.value_objects import BookId


class BookAssetRepository(ABC):
    @abstractmethod
    async def save(self, asset: BookAsset) -> None: ...

    @abstractmethod
    async def get(self, asset_id: BookAssetId) -> BookAsset | None: ...

    @abstractmethod
    async def get_by_sha256(self, sha256: Sha256) -> BookAsset | None: ...

    @abstractmethod
    async def for_book(self, book_id: BookId) -> BookAsset | None:
        """Resolve the primary asset for a canonical book.

        Only place that speaks `Book -> BookAsset`. Callers MUST use this
        resolver instead of reading `books.primary_asset_id` directly so that
        adding multi-format support later (`book_formats`) only changes this
        method, not every use case.
        """

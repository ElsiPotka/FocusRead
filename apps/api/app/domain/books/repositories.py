from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.book_asset.value_objects import BookAssetId
    from app.domain.books.entities import Book
    from app.domain.books.filter import BookFilter
    from app.domain.books.value_objects import BookId


class BookRepository(ABC):
    """Canonical catalog book persistence.

    Slim interface: books are catalog records, not user-owned uploads.
    Reader access queries belong on `LibraryItemRepository`; merchant
    queries belong on `MarketplaceListingRepository`. This interface only
    speaks in catalog identity and metadata.
    """

    @abstractmethod
    async def save(self, book: Book) -> None: ...

    @abstractmethod
    async def get(self, book_id: BookId) -> Book | None: ...

    @abstractmethod
    async def get_for_owner(
        self, *, book_id: BookId, owner_user_id: UserId
    ) -> Book | None: ...

    @abstractmethod
    async def list_for_owner(self, *, owner_user_id: UserId) -> list[Book]: ...

    @abstractmethod
    async def search(self, *, book_filter: BookFilter) -> list[Book]: ...

    @abstractmethod
    async def list_by_ids(self, book_ids: list[BookId]) -> list[Book]: ...

    @abstractmethod
    async def count_referencing_asset(self, *, asset_id: BookAssetId) -> int:
        """Count catalog books whose `primary_asset_id` points at this asset.

        Used to decide whether an asset blob can be torn down. As long as
        any book references the asset (via `books.primary_asset_id`), the
        asset row and storage blob must be retained — the FK uses
        `ON DELETE RESTRICT` at the schema level, so this check prevents
        integrity errors at the application layer.
        """

    @abstractmethod
    async def delete(self, *, book_id: BookId) -> None: ...

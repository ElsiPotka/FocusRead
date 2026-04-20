from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

from app.infrastructure.logging.logger import log

if TYPE_CHECKING:
    from app.domain.auth.repositories import (
        AccountRepository,
        JWTSigningKeyRepository,
        SessionRepository,
        UserRepository,
    )
    from app.domain.book_asset.repositories import BookAssetRepository
    from app.domain.book_chunks.repositories import BookChunkRepository
    from app.domain.book_toc_entry.repositories import BookTOCEntryRepository
    from app.domain.bookmark.repositories import BookmarkRepository
    from app.domain.books.repositories import BookRepository
    from app.domain.contributor.repositories import ContributorRepository
    from app.domain.label.repositories import LabelRepository
    from app.domain.library_item.repositories import LibraryItemRepository
    from app.domain.marketplace_listing.repositories import (
        MarketplaceListingRepository,
    )
    from app.domain.reading_sessions.repositories import ReadingSessionRepository
    from app.domain.reading_stats.repositories import ReadingStatRepository
    from app.domain.role.repositories import RoleRepository
    from app.domain.shelf.repositories import ShelfRepository
    from app.domain.theme.repositories import ThemeRepository


class AbstractUnitOfWork(ABC):
    books: BookRepository
    book_assets: BookAssetRepository
    book_chunks: BookChunkRepository
    book_toc_entries: BookTOCEntryRepository
    bookmarks: BookmarkRepository
    contributors: ContributorRepository
    labels: LabelRepository
    library_items: LibraryItemRepository
    marketplace_listings: MarketplaceListingRepository
    reading_sessions: ReadingSessionRepository
    reading_stats: ReadingStatRepository
    shelves: ShelfRepository
    themes: ThemeRepository
    users: UserRepository
    roles: RoleRepository
    accounts: AccountRepository
    sessions: SessionRepository
    jwt_signing_keys: JWTSigningKeyRepository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            log.opt(exception=(exc_type, exc_val, exc_tb)).warning(
                "Rolling back transaction due to an exception.",
            )
            await self.rollback()

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

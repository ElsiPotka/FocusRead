from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId
    from app.domain.marketplace_listing.entities import MarketplaceListing
    from app.domain.marketplace_listing.value_objects import (
        ListingSlug,
        MarketplaceListingId,
    )


class MarketplaceListingRepository(ABC):
    @abstractmethod
    async def save(self, listing: MarketplaceListing) -> None: ...

    @abstractmethod
    async def get(
        self, listing_id: MarketplaceListingId
    ) -> MarketplaceListing | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: ListingSlug) -> MarketplaceListing | None: ...

    @abstractmethod
    async def get_active_for_merchant_book(
        self, *, merchant_user_id: UserId, book_id: BookId
    ) -> MarketplaceListing | None:
        """Return the merchant's non-archived listing for a book, if any.

        Backed by the partial unique index
        `WHERE status <> 'archived'` on `(merchant_user_id, book_id)`.
        """

    @abstractmethod
    async def list_for_merchant(
        self, *, merchant_user_id: UserId
    ) -> list[MarketplaceListing]: ...

    @abstractmethod
    async def delete(self, *, listing_id: MarketplaceListingId) -> None: ...

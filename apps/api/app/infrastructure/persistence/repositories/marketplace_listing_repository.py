from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select

from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.marketplace_listing.entities import MarketplaceListing
from app.domain.marketplace_listing.repositories import MarketplaceListingRepository
from app.domain.marketplace_listing.value_objects import (
    ListingSlug,
    ListingSourceRef,
    ListingStatus,
    MarketplaceListingId,
    ModerationStatus,
)
from app.infrastructure.persistence.models.marketplace_listing import (
    MarketplaceListingModel,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyMarketplaceListingRepository(MarketplaceListingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, listing: MarketplaceListing) -> None:
        model = await self.session.get(MarketplaceListingModel, listing.id.value)
        if model is None:
            model = MarketplaceListingModel(
                id=listing.id.value,
                merchant_user_id=listing.merchant_user_id.value,
                book_id=listing.book_id.value,
                slug=listing.slug.value,
                status=listing.status.value,
                moderation_status=listing.moderation_status.value,
                published_at=listing.published_at,
                unpublished_at=listing.unpublished_at,
                featured_at=listing.featured_at,
                source_ref=(
                    listing.source_ref.value if listing.source_ref is not None else None
                ),
                created_at=listing.created_at,
                updated_at=listing.updated_at,
            )
            self.session.add(model)
            return

        model.slug = listing.slug.value
        model.status = listing.status.value
        model.moderation_status = listing.moderation_status.value
        model.published_at = listing.published_at
        model.unpublished_at = listing.unpublished_at
        model.featured_at = listing.featured_at
        model.source_ref = (
            listing.source_ref.value if listing.source_ref is not None else None
        )
        model.updated_at = listing.updated_at

    async def get(self, listing_id: MarketplaceListingId) -> MarketplaceListing | None:
        model = await self.session.get(MarketplaceListingModel, listing_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_slug(self, slug: ListingSlug) -> MarketplaceListing | None:
        stmt = select(MarketplaceListingModel).where(
            MarketplaceListingModel.slug == slug.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_active_for_merchant_book(
        self, *, merchant_user_id: UserId, book_id: BookId
    ) -> MarketplaceListing | None:
        stmt = select(MarketplaceListingModel).where(
            MarketplaceListingModel.merchant_user_id == merchant_user_id.value,
            MarketplaceListingModel.book_id == book_id.value,
            MarketplaceListingModel.status != ListingStatus.ARCHIVED.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_merchant(
        self, *, merchant_user_id: UserId
    ) -> list[MarketplaceListing]:
        stmt = select(MarketplaceListingModel).where(
            MarketplaceListingModel.merchant_user_id == merchant_user_id.value,
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_active_for_book(self, *, book_id: BookId) -> int:
        stmt = (
            select(func.count())
            .select_from(MarketplaceListingModel)
            .where(
                MarketplaceListingModel.book_id == book_id.value,
                MarketplaceListingModel.status != ListingStatus.ARCHIVED.value,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, *, listing_id: MarketplaceListingId) -> None:
        model = await self.session.get(MarketplaceListingModel, listing_id.value)
        if model is not None:
            await self.session.delete(model)

    @staticmethod
    def _to_entity(model: MarketplaceListingModel) -> MarketplaceListing:
        return MarketplaceListing(
            id=MarketplaceListingId(model.id),
            merchant_user_id=UserId(model.merchant_user_id),
            book_id=BookId(model.book_id),
            slug=ListingSlug(model.slug),
            status=ListingStatus(model.status),
            moderation_status=ModerationStatus(model.moderation_status),
            published_at=model.published_at,
            unpublished_at=model.unpublished_at,
            featured_at=model.featured_at,
            source_ref=(
                ListingSourceRef(model.source_ref)
                if model.source_ref is not None
                else None
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

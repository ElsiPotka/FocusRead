from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.library_item.entities import LibraryItem
from app.domain.library_item.repositories import LibraryItemRepository
from app.domain.library_item.value_objects import (
    AccessStatus,
    LibraryItemId,
    LibrarySourceKind,
    LibrarySourceRef,
    PreferredWordsPerFlash,
    PreferredWPM,
    RevocationReason,
)
from app.domain.marketplace_listing.value_objects import MarketplaceListingId
from app.infrastructure.persistence.models.library_item import LibraryItemModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyLibraryItemRepository(LibraryItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, item: LibraryItem) -> None:
        model = await self.session.get(LibraryItemModel, item.id.value)
        if model is None:
            model = LibraryItemModel(
                id=item.id.value,
                user_id=item.user_id.value,
                book_id=item.book_id.value,
                source_listing_id=(
                    item.source_listing_id.value
                    if item.source_listing_id is not None
                    else None
                ),
                source_kind=item.source_kind.value,
                source_ref=(
                    item.source_ref.value if item.source_ref is not None else None
                ),
                access_status=item.access_status.value,
                acquired_at=item.acquired_at,
                expires_at=item.expires_at,
                revoked_at=item.revoked_at,
                revocation_reason=(
                    item.revocation_reason.value
                    if item.revocation_reason is not None
                    else None
                ),
                favorited_at=item.favorited_at,
                archived_at=item.archived_at,
                completed_at=item.completed_at,
                last_opened_at=item.last_opened_at,
                preferred_wpm=(
                    item.preferred_wpm.value if item.preferred_wpm is not None else None
                ),
                preferred_words_per_flash=(
                    item.preferred_words_per_flash.value
                    if item.preferred_words_per_flash is not None
                    else None
                ),
                skip_images=item.skip_images,
                ramp_up_enabled=item.ramp_up_enabled,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            self.session.add(model)
            return

        model.source_listing_id = (
            item.source_listing_id.value if item.source_listing_id is not None else None
        )
        model.source_kind = item.source_kind.value
        model.source_ref = (
            item.source_ref.value if item.source_ref is not None else None
        )
        model.access_status = item.access_status.value
        model.acquired_at = item.acquired_at
        model.expires_at = item.expires_at
        model.revoked_at = item.revoked_at
        model.revocation_reason = (
            item.revocation_reason.value if item.revocation_reason is not None else None
        )
        model.favorited_at = item.favorited_at
        model.archived_at = item.archived_at
        model.completed_at = item.completed_at
        model.last_opened_at = item.last_opened_at
        model.preferred_wpm = (
            item.preferred_wpm.value if item.preferred_wpm is not None else None
        )
        model.preferred_words_per_flash = (
            item.preferred_words_per_flash.value
            if item.preferred_words_per_flash is not None
            else None
        )
        model.skip_images = item.skip_images
        model.ramp_up_enabled = item.ramp_up_enabled
        model.updated_at = item.updated_at

    async def get(self, item_id: LibraryItemId) -> LibraryItem | None:
        model = await self.session.get(LibraryItemModel, item_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_active_for_user_book(
        self, *, user_id: UserId, book_id: BookId
    ) -> LibraryItem | None:
        stmt = select(LibraryItemModel).where(
            LibraryItemModel.user_id == user_id.value,
            LibraryItemModel.book_id == book_id.value,
            LibraryItemModel.access_status == AccessStatus.ACTIVE.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_user(self, *, user_id: UserId) -> list[LibraryItem]:
        stmt = select(LibraryItemModel).where(
            LibraryItemModel.user_id == user_id.value,
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def delete(self, *, item_id: LibraryItemId) -> None:
        model = await self.session.get(LibraryItemModel, item_id.value)
        if model is not None:
            await self.session.delete(model)

    @staticmethod
    def _to_entity(model: LibraryItemModel) -> LibraryItem:
        return LibraryItem(
            id=LibraryItemId(model.id),
            user_id=UserId(model.user_id),
            book_id=BookId(model.book_id),
            source_kind=LibrarySourceKind(model.source_kind),
            source_listing_id=(
                MarketplaceListingId(model.source_listing_id)
                if model.source_listing_id is not None
                else None
            ),
            source_ref=(
                LibrarySourceRef(model.source_ref)
                if model.source_ref is not None
                else None
            ),
            access_status=AccessStatus(model.access_status),
            acquired_at=model.acquired_at,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            revocation_reason=(
                RevocationReason(model.revocation_reason)
                if model.revocation_reason is not None
                else None
            ),
            favorited_at=model.favorited_at,
            archived_at=model.archived_at,
            completed_at=model.completed_at,
            last_opened_at=model.last_opened_at,
            preferred_wpm=(
                PreferredWPM(model.preferred_wpm)
                if model.preferred_wpm is not None
                else None
            ),
            preferred_words_per_flash=(
                PreferredWordsPerFlash(model.preferred_words_per_flash)
                if model.preferred_words_per_flash is not None
                else None
            ),
            skip_images=model.skip_images,
            ramp_up_enabled=model.ramp_up_enabled,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

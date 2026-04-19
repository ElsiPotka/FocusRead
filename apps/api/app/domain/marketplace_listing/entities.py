from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.domain.marketplace_listing.errors import InvalidListingStateError
from app.domain.marketplace_listing.value_objects import (
    ListingSlug,
    ListingSourceRef,
    ListingStatus,
    MarketplaceListingId,
    ModerationStatus,
)

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId


class MarketplaceListing:
    """Merchant-facing marketplace offer for a catalog Book.

    A listing is the sales unit; readable content and per-user state belong
    to `Book` and `LibraryItem` respectively. A merchant may have at most
    one non-archived listing per book (enforced by a partial unique index).
    """

    def __init__(
        self,
        *,
        id: MarketplaceListingId,
        merchant_user_id: UserId,
        book_id: BookId,
        slug: ListingSlug,
        status: ListingStatus = ListingStatus.DRAFT,
        moderation_status: ModerationStatus = ModerationStatus.PENDING,
        published_at: datetime | None = None,
        unpublished_at: datetime | None = None,
        featured_at: datetime | None = None,
        source_ref: ListingSourceRef | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        now = datetime.now(UTC)
        self._id = id
        self._merchant_user_id = merchant_user_id
        self._book_id = book_id
        self._slug = slug
        self._status = status
        self._moderation_status = moderation_status
        self._published_at = published_at
        self._unpublished_at = unpublished_at
        self._featured_at = featured_at
        self._source_ref = source_ref
        self._created_at = created_at or now
        self._updated_at = updated_at or now

    @classmethod
    def create(
        cls,
        *,
        merchant_user_id: UserId,
        book_id: BookId,
        slug: ListingSlug,
        source_ref: ListingSourceRef | None = None,
    ) -> MarketplaceListing:
        return cls(
            id=MarketplaceListingId.generate(),
            merchant_user_id=merchant_user_id,
            book_id=book_id,
            slug=slug,
            status=ListingStatus.DRAFT,
            moderation_status=ModerationStatus.PENDING,
            source_ref=source_ref,
        )

    @property
    def id(self) -> MarketplaceListingId:
        return self._id

    @property
    def merchant_user_id(self) -> UserId:
        return self._merchant_user_id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def slug(self) -> ListingSlug:
        return self._slug

    @property
    def status(self) -> ListingStatus:
        return self._status

    @property
    def moderation_status(self) -> ModerationStatus:
        return self._moderation_status

    @property
    def published_at(self) -> datetime | None:
        return self._published_at

    @property
    def unpublished_at(self) -> datetime | None:
        return self._unpublished_at

    @property
    def featured_at(self) -> datetime | None:
        return self._featured_at

    @property
    def source_ref(self) -> ListingSourceRef | None:
        return self._source_ref

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def is_live(self) -> bool:
        """True if the listing is publicly visible on the marketplace."""
        return (
            self._status is ListingStatus.PUBLISHED
            and self._moderation_status is ModerationStatus.APPROVED
        )

    def rename_slug(self, slug: ListingSlug) -> None:
        if self._status is ListingStatus.ARCHIVED:
            raise InvalidListingStateError(
                "Cannot rename the slug of an archived listing.",
            )
        self._slug = slug
        self._updated_at = datetime.now(UTC)

    def publish(self, *, at: datetime | None = None) -> None:
        if self._status is ListingStatus.ARCHIVED:
            raise InvalidListingStateError("Cannot publish an archived listing.")
        if self._moderation_status is not ModerationStatus.APPROVED:
            raise InvalidListingStateError(
                "Listing must be approved before it can be published.",
            )
        if self._status is ListingStatus.PUBLISHED:
            return
        now = at or datetime.now(UTC)
        self._status = ListingStatus.PUBLISHED
        self._published_at = now
        self._unpublished_at = None
        self._updated_at = now

    def hide(self, *, at: datetime | None = None) -> None:
        if self._status is ListingStatus.ARCHIVED:
            raise InvalidListingStateError("Cannot hide an archived listing.")
        if self._status is ListingStatus.HIDDEN:
            return
        now = at or datetime.now(UTC)
        self._status = ListingStatus.HIDDEN
        self._unpublished_at = now
        self._updated_at = now

    def unpublish(self, *, at: datetime | None = None) -> None:
        if self._status is ListingStatus.ARCHIVED:
            raise InvalidListingStateError("Cannot unpublish an archived listing.")
        if self._status is ListingStatus.DRAFT:
            return
        now = at or datetime.now(UTC)
        self._status = ListingStatus.DRAFT
        self._unpublished_at = now
        self._updated_at = now

    def archive(self, *, at: datetime | None = None) -> None:
        if self._status is ListingStatus.ARCHIVED:
            return
        now = at or datetime.now(UTC)
        self._status = ListingStatus.ARCHIVED
        self._unpublished_at = self._unpublished_at or now
        self._featured_at = None
        self._updated_at = now

    def approve_moderation(self) -> None:
        if self._moderation_status is ModerationStatus.APPROVED:
            return
        self._moderation_status = ModerationStatus.APPROVED
        self._updated_at = datetime.now(UTC)

    def reject_moderation(self) -> None:
        """Admin reject: listing stays out of the public marketplace.

        If the listing was published, it is demoted to hidden so callers do
        not need a second mutation to pull it from browse results.
        """
        self._moderation_status = ModerationStatus.REJECTED
        if self._status is ListingStatus.PUBLISHED:
            now = datetime.now(UTC)
            self._status = ListingStatus.HIDDEN
            self._unpublished_at = now
        self._updated_at = datetime.now(UTC)

    def reset_moderation_to_pending(self) -> None:
        if self._moderation_status is ModerationStatus.PENDING:
            return
        self._moderation_status = ModerationStatus.PENDING
        self._updated_at = datetime.now(UTC)

    def feature(self, *, at: datetime | None = None) -> None:
        if not self.is_live():
            raise InvalidListingStateError(
                "Only live (published + approved) listings can be featured.",
            )
        self._featured_at = at or datetime.now(UTC)
        self._updated_at = datetime.now(UTC)

    def unfeature(self) -> None:
        if self._featured_at is None:
            return
        self._featured_at = None
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MarketplaceListing) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

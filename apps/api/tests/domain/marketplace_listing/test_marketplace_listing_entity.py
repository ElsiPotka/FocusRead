from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.marketplace_listing.entities import MarketplaceListing
from app.domain.marketplace_listing.errors import InvalidListingStateError
from app.domain.marketplace_listing.value_objects import (
    ListingSlug,
    ListingSourceRef,
    ListingStatus,
    ModerationStatus,
)


def _make_listing(
    *,
    merchant_user_id: UserId | None = None,
    book_id: BookId | None = None,
    slug: ListingSlug | None = None,
    source_ref: ListingSourceRef | None = None,
) -> MarketplaceListing:
    return MarketplaceListing.create(
        merchant_user_id=merchant_user_id or UserId(uuid4()),
        book_id=book_id or BookId(uuid4()),
        slug=slug or ListingSlug("deep-work"),
        source_ref=source_ref,
    )


def _approved(listing: MarketplaceListing) -> MarketplaceListing:
    listing.approve_moderation()
    return listing


class TestCreation:
    def test_defaults_are_draft_pending(self):
        listing = _make_listing()

        assert listing.status is ListingStatus.DRAFT
        assert listing.moderation_status is ModerationStatus.PENDING
        assert listing.is_live() is False
        assert listing.published_at is None
        assert listing.unpublished_at is None
        assert listing.featured_at is None

    def test_generates_id_and_timestamps(self):
        listing = _make_listing()

        assert listing.id is not None
        assert listing.created_at is not None
        assert listing.updated_at is not None

    def test_captures_source_ref(self):
        ref = ListingSourceRef("ext:123")
        listing = _make_listing(source_ref=ref)

        assert listing.source_ref == ref


class TestPublish:
    def test_requires_approval(self):
        listing = _make_listing()

        with pytest.raises(InvalidListingStateError, match="approved"):
            listing.publish()

    def test_approved_listing_publishes(self):
        listing = _approved(_make_listing())

        listing.publish()

        assert listing.status is ListingStatus.PUBLISHED
        assert listing.published_at is not None
        assert listing.unpublished_at is None
        assert listing.is_live() is True

    def test_publish_is_idempotent(self):
        listing = _approved(_make_listing())
        listing.publish()
        first_published_at = listing.published_at

        listing.publish()

        assert listing.published_at == first_published_at

    def test_cannot_publish_archived(self):
        listing = _approved(_make_listing())
        listing.archive()

        with pytest.raises(InvalidListingStateError, match="archived"):
            listing.publish()


class TestHideAndUnpublish:
    def test_hide_moves_published_to_hidden(self):
        listing = _approved(_make_listing())
        listing.publish()

        listing.hide()

        assert listing.status is ListingStatus.HIDDEN
        assert listing.unpublished_at is not None
        assert listing.is_live() is False

    def test_hide_is_idempotent(self):
        listing = _approved(_make_listing())
        listing.publish()
        listing.hide()
        first_updated = listing.updated_at

        listing.hide()

        assert listing.updated_at == first_updated

    def test_unpublish_returns_to_draft(self):
        listing = _approved(_make_listing())
        listing.publish()

        listing.unpublish()

        assert listing.status is ListingStatus.DRAFT
        assert listing.unpublished_at is not None

    def test_unpublish_from_draft_is_noop(self):
        listing = _make_listing()
        first_updated = listing.updated_at

        listing.unpublish()

        assert listing.updated_at == first_updated

    def test_cannot_hide_archived(self):
        listing = _approved(_make_listing())
        listing.archive()

        with pytest.raises(InvalidListingStateError, match="archived"):
            listing.hide()


class TestArchive:
    def test_archive_clears_featured(self):
        listing = _approved(_make_listing())
        listing.publish()
        listing.feature()

        listing.archive()

        assert listing.status is ListingStatus.ARCHIVED
        assert listing.featured_at is None
        assert listing.unpublished_at is not None

    def test_archive_is_idempotent(self):
        listing = _make_listing()
        listing.archive()
        first_updated = listing.updated_at

        listing.archive()

        assert listing.updated_at == first_updated

    def test_rename_slug_rejected_on_archived(self):
        listing = _make_listing()
        listing.archive()

        with pytest.raises(InvalidListingStateError, match="archived"):
            listing.rename_slug(ListingSlug("another-slug"))


class TestModeration:
    def test_approve_flips_status(self):
        listing = _make_listing()

        listing.approve_moderation()

        assert listing.moderation_status is ModerationStatus.APPROVED

    def test_approve_is_idempotent(self):
        listing = _approved(_make_listing())
        first_updated = listing.updated_at

        listing.approve_moderation()

        assert listing.updated_at == first_updated

    def test_reject_demotes_published_to_hidden(self):
        listing = _approved(_make_listing())
        listing.publish()

        listing.reject_moderation()

        assert listing.moderation_status is ModerationStatus.REJECTED
        assert listing.status is ListingStatus.HIDDEN
        assert listing.unpublished_at is not None

    def test_reject_on_draft_leaves_status(self):
        listing = _make_listing()

        listing.reject_moderation()

        assert listing.moderation_status is ModerationStatus.REJECTED
        assert listing.status is ListingStatus.DRAFT

    def test_reset_to_pending(self):
        listing = _approved(_make_listing())

        listing.reset_moderation_to_pending()

        assert listing.moderation_status is ModerationStatus.PENDING


class TestFeature:
    def test_feature_requires_live(self):
        listing = _make_listing()

        with pytest.raises(InvalidListingStateError, match="live"):
            listing.feature()

    def test_feature_on_live_listing(self):
        listing = _approved(_make_listing())
        listing.publish()

        listing.feature()

        assert listing.featured_at is not None

    def test_unfeature(self):
        listing = _approved(_make_listing())
        listing.publish()
        listing.feature()

        listing.unfeature()

        assert listing.featured_at is None

    def test_unfeature_when_not_featured_is_noop(self):
        listing = _approved(_make_listing())
        listing.publish()
        first_updated = listing.updated_at

        listing.unfeature()

        assert listing.updated_at == first_updated


class TestRenameSlug:
    def test_renames(self):
        listing = _make_listing(slug=ListingSlug("original"))

        listing.rename_slug(ListingSlug("updated"))

        assert listing.slug == ListingSlug("updated")


class TestEquality:
    def test_equal_by_id(self):
        listing = _make_listing()
        other_view = MarketplaceListing(
            id=listing.id,
            merchant_user_id=UserId(uuid4()),
            book_id=BookId(uuid4()),
            slug=ListingSlug("something-else"),
        )

        assert listing == other_view
        assert hash(listing) == hash(other_view)

from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.library_item.entities import LibraryItem
from app.domain.library_item.errors import InvalidLibraryItemStateError
from app.domain.library_item.value_objects import (
    AccessStatus,
    LibrarySourceKind,
    LibrarySourceRef,
    PreferredWordsPerFlash,
    PreferredWPM,
    RevocationReason,
)
from app.domain.marketplace_listing.value_objects import MarketplaceListingId


def _make_item(
    *,
    user_id: UserId | None = None,
    book_id: BookId | None = None,
    source_kind: LibrarySourceKind = LibrarySourceKind.UPLOAD,
    source_listing_id: MarketplaceListingId | None = None,
    source_ref: LibrarySourceRef | None = None,
) -> LibraryItem:
    return LibraryItem.create(
        user_id=user_id or UserId(uuid4()),
        book_id=book_id or BookId(uuid4()),
        source_kind=source_kind,
        source_listing_id=source_listing_id,
        source_ref=source_ref,
    )


class TestLibraryItemCreation:
    def test_defaults_are_active_and_unset(self):
        item = _make_item()

        assert item.access_status is AccessStatus.ACTIVE
        assert item.is_readable() is True
        assert item.favorited_at is None
        assert item.archived_at is None
        assert item.completed_at is None
        assert item.last_opened_at is None
        assert item.revoked_at is None
        assert item.revocation_reason is None
        assert item.skip_images is False
        assert item.ramp_up_enabled is True

    def test_generates_id_and_timestamps(self):
        item = _make_item()

        assert item.id is not None
        assert item.created_at is not None
        assert item.updated_at is not None
        assert item.acquired_at is not None

    def test_captures_source_metadata(self):
        listing_id = MarketplaceListingId.generate()
        ref = LibrarySourceRef("purchase:abc123")

        item = _make_item(
            source_kind=LibrarySourceKind.PURCHASE,
            source_listing_id=listing_id,
            source_ref=ref,
        )

        assert item.source_kind is LibrarySourceKind.PURCHASE
        assert item.source_listing_id == listing_id
        assert item.source_ref == ref


class TestAccessStatusTransitions:
    def test_revoke_sets_status_and_metadata(self):
        item = _make_item()
        reason = RevocationReason("chargeback")

        item.revoke(reason=reason)

        assert item.access_status is AccessStatus.REVOKED
        assert item.is_readable() is False
        assert item.revoked_at is not None
        assert item.revocation_reason == reason

    def test_revoke_is_idempotent(self):
        item = _make_item()
        item.revoke(reason=RevocationReason("x"))
        first_revoked_at = item.revoked_at

        item.revoke(reason=RevocationReason("y"))

        assert item.revoked_at == first_revoked_at

    def test_expire_sets_status(self):
        item = _make_item()

        item.expire()

        assert item.access_status is AccessStatus.EXPIRED
        assert item.is_readable() is False

    def test_expire_is_idempotent(self):
        item = _make_item()
        item.expire()
        first_updated = item.updated_at

        item.expire()

        assert item.updated_at == first_updated

    def test_reactivate_from_revoked_clears_revocation(self):
        item = _make_item()
        item.revoke(reason=RevocationReason("chargeback"))

        item.reactivate()

        assert item.access_status is AccessStatus.ACTIVE
        assert item.revoked_at is None
        assert item.revocation_reason is None

    def test_reactivate_from_active_noop(self):
        item = _make_item()
        before = item.updated_at

        item.reactivate()

        assert item.updated_at == before


class TestUpgradeSourceKind:
    def test_merchant_as_buyer_upgrades_in_place(self):
        item = _make_item(source_kind=LibrarySourceKind.UPLOAD)
        listing_id = MarketplaceListingId.generate()

        item.upgrade_source_kind(
            source_kind=LibrarySourceKind.SELLER_COPY,
            source_listing_id=listing_id,
        )

        assert item.source_kind is LibrarySourceKind.SELLER_COPY
        assert item.source_listing_id == listing_id

    def test_upgrade_refuses_on_revoked_item(self):
        item = _make_item()
        item.revoke(reason=RevocationReason("x"))

        with pytest.raises(InvalidLibraryItemStateError):
            item.upgrade_source_kind(source_kind=LibrarySourceKind.SELLER_COPY)


class TestReaderFlags:
    def test_favorite_and_unfavorite(self):
        item = _make_item()

        item.favorite()
        assert item.favorited_at is not None

        item.unfavorite()
        assert item.favorited_at is None

    def test_archive_and_unarchive(self):
        item = _make_item()

        item.archive()
        assert item.archived_at is not None

        item.unarchive()
        assert item.archived_at is None

    def test_mark_completed_and_reopen(self):
        item = _make_item()

        item.mark_completed()
        assert item.completed_at is not None

        item.reopen()
        assert item.completed_at is None

    def test_record_opened_sets_last_opened(self):
        item = _make_item()

        item.record_opened()

        assert item.last_opened_at is not None

    @pytest.mark.parametrize(
        "action",
        ["favorite", "archive", "mark_completed", "record_opened"],
    )
    def test_reader_actions_require_active(self, action: str):
        item = _make_item()
        item.revoke(reason=RevocationReason("x"))

        with pytest.raises(InvalidLibraryItemStateError):
            getattr(item, action)()


class TestUpdatePreferences:
    def test_sets_only_provided_fields(self):
        item = _make_item()

        item.update_preferences(preferred_wpm=PreferredWPM(400))

        assert item.preferred_wpm == PreferredWPM(400)
        assert item.preferred_words_per_flash is None
        assert item.skip_images is False
        assert item.ramp_up_enabled is True

    def test_unset_fields_are_preserved(self):
        item = _make_item()
        item.update_preferences(preferred_wpm=PreferredWPM(400))

        item.update_preferences(
            preferred_words_per_flash=PreferredWordsPerFlash(2),
        )

        assert item.preferred_wpm == PreferredWPM(400)
        assert item.preferred_words_per_flash == PreferredWordsPerFlash(2)

    def test_can_explicitly_clear_to_none(self):
        item = _make_item()
        item.update_preferences(preferred_wpm=PreferredWPM(400))

        item.update_preferences(preferred_wpm=None)

        assert item.preferred_wpm is None

    def test_toggles_booleans(self):
        item = _make_item()

        item.update_preferences(skip_images=True, ramp_up_enabled=False)

        assert item.skip_images is True
        assert item.ramp_up_enabled is False


class TestEquality:
    def test_equal_by_id(self):
        item = _make_item()
        other_view = LibraryItem(
            id=item.id,
            user_id=UserId(uuid4()),
            book_id=BookId(uuid4()),
            source_kind=LibrarySourceKind.UPLOAD,
        )

        assert item == other_view
        assert hash(item) == hash(other_view)

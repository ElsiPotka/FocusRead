from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, cast

from app.domain.library_item.errors import InvalidLibraryItemStateError
from app.domain.library_item.value_objects import (
    AccessStatus,
    LibraryItemId,
    LibrarySourceKind,
    LibrarySourceRef,
    PreferredWordsPerFlash,
    PreferredWPM,
    RevocationReason,
)

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId
    from app.domain.marketplace_listing.value_objects import MarketplaceListingId

_UNSET: Final = object()


class LibraryItem:
    """The user's readable copy of a catalog Book.

    Owns both access (source_kind, access_status, acquired_at, expires_at,
    revoked_at) and per-user reader state (favorite, archived, completed,
    last_opened, reading preferences). Replaces the old user_book_state
    aggregate.
    """

    def __init__(
        self,
        *,
        id: LibraryItemId,
        user_id: UserId,
        book_id: BookId,
        source_kind: LibrarySourceKind,
        source_listing_id: MarketplaceListingId | None = None,
        source_ref: LibrarySourceRef | None = None,
        access_status: AccessStatus = AccessStatus.ACTIVE,
        acquired_at: datetime | None = None,
        expires_at: datetime | None = None,
        revoked_at: datetime | None = None,
        revocation_reason: RevocationReason | None = None,
        favorited_at: datetime | None = None,
        archived_at: datetime | None = None,
        completed_at: datetime | None = None,
        last_opened_at: datetime | None = None,
        preferred_wpm: PreferredWPM | None = None,
        preferred_words_per_flash: PreferredWordsPerFlash | None = None,
        skip_images: bool = False,
        ramp_up_enabled: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        now = datetime.now(UTC)
        self._id = id
        self._user_id = user_id
        self._book_id = book_id
        self._source_kind = source_kind
        self._source_listing_id = source_listing_id
        self._source_ref = source_ref
        self._access_status = access_status
        self._acquired_at = acquired_at or now
        self._expires_at = expires_at
        self._revoked_at = revoked_at
        self._revocation_reason = revocation_reason
        self._favorited_at = favorited_at
        self._archived_at = archived_at
        self._completed_at = completed_at
        self._last_opened_at = last_opened_at
        self._preferred_wpm = preferred_wpm
        self._preferred_words_per_flash = preferred_words_per_flash
        self._skip_images = skip_images
        self._ramp_up_enabled = ramp_up_enabled
        self._created_at = created_at or now
        self._updated_at = updated_at or now

    @classmethod
    def create(
        cls,
        *,
        user_id: UserId,
        book_id: BookId,
        source_kind: LibrarySourceKind,
        source_listing_id: MarketplaceListingId | None = None,
        source_ref: LibrarySourceRef | None = None,
    ) -> LibraryItem:
        return cls(
            id=LibraryItemId.generate(),
            user_id=user_id,
            book_id=book_id,
            source_kind=source_kind,
            source_listing_id=source_listing_id,
            source_ref=source_ref,
            access_status=AccessStatus.ACTIVE,
        )

    @property
    def id(self) -> LibraryItemId:
        return self._id

    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def source_kind(self) -> LibrarySourceKind:
        return self._source_kind

    @property
    def source_listing_id(self) -> MarketplaceListingId | None:
        return self._source_listing_id

    @property
    def source_ref(self) -> LibrarySourceRef | None:
        return self._source_ref

    @property
    def access_status(self) -> AccessStatus:
        return self._access_status

    @property
    def acquired_at(self) -> datetime:
        return self._acquired_at

    @property
    def expires_at(self) -> datetime | None:
        return self._expires_at

    @property
    def revoked_at(self) -> datetime | None:
        return self._revoked_at

    @property
    def revocation_reason(self) -> RevocationReason | None:
        return self._revocation_reason

    @property
    def favorited_at(self) -> datetime | None:
        return self._favorited_at

    @property
    def archived_at(self) -> datetime | None:
        return self._archived_at

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    @property
    def last_opened_at(self) -> datetime | None:
        return self._last_opened_at

    @property
    def preferred_wpm(self) -> PreferredWPM | None:
        return self._preferred_wpm

    @property
    def preferred_words_per_flash(self) -> PreferredWordsPerFlash | None:
        return self._preferred_words_per_flash

    @property
    def skip_images(self) -> bool:
        return self._skip_images

    @property
    def ramp_up_enabled(self) -> bool:
        return self._ramp_up_enabled

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def is_readable(self) -> bool:
        return self._access_status is AccessStatus.ACTIVE

    def upgrade_source_kind(
        self,
        *,
        source_kind: LibrarySourceKind,
        source_listing_id: MarketplaceListingId | None = None,
        source_ref: LibrarySourceRef | None = None,
    ) -> None:
        """Transition provenance in place — e.g. upload -> seller_copy.

        Invariant from BOOK_MARKETPLACE_PLAN: if a merchant already holds an
        active LibraryItem for a book they later list, we do NOT create a
        second active row; we upgrade the existing one. Only callable while
        the item is still active — revoked/expired rows must be re-acquired.
        """
        if self._access_status is not AccessStatus.ACTIVE:
            raise InvalidLibraryItemStateError(
                "Only active library items can have their source upgraded.",
            )
        self._source_kind = source_kind
        if source_listing_id is not None:
            self._source_listing_id = source_listing_id
        if source_ref is not None:
            self._source_ref = source_ref
        self._updated_at = datetime.now(UTC)

    def revoke(
        self,
        *,
        reason: RevocationReason | None = None,
        at: datetime | None = None,
    ) -> None:
        if self._access_status is AccessStatus.REVOKED:
            return
        now = at or datetime.now(UTC)
        self._access_status = AccessStatus.REVOKED
        self._revoked_at = now
        self._revocation_reason = reason
        self._updated_at = now

    def expire(self, *, at: datetime | None = None) -> None:
        if self._access_status is AccessStatus.EXPIRED:
            return
        now = at or datetime.now(UTC)
        self._access_status = AccessStatus.EXPIRED
        self._updated_at = now

    def reactivate(self) -> None:
        if self._access_status is AccessStatus.ACTIVE:
            return
        self._access_status = AccessStatus.ACTIVE
        self._revoked_at = None
        self._revocation_reason = None
        self._updated_at = datetime.now(UTC)

    def favorite(self, *, at: datetime | None = None) -> None:
        self._require_active("favorite")
        self._favorited_at = at or datetime.now(UTC)
        self._updated_at = datetime.now(UTC)

    def unfavorite(self) -> None:
        self._favorited_at = None
        self._updated_at = datetime.now(UTC)

    def archive(self, *, at: datetime | None = None) -> None:
        self._require_active("archive")
        self._archived_at = at or datetime.now(UTC)
        self._updated_at = datetime.now(UTC)

    def unarchive(self) -> None:
        self._archived_at = None
        self._updated_at = datetime.now(UTC)

    def mark_completed(self, *, at: datetime | None = None) -> None:
        self._require_active("mark_completed")
        self._completed_at = at or datetime.now(UTC)
        self._updated_at = datetime.now(UTC)

    def reopen(self) -> None:
        self._completed_at = None
        self._updated_at = datetime.now(UTC)

    def record_opened(self, *, at: datetime | None = None) -> None:
        self._require_active("record_opened")
        self._last_opened_at = at or datetime.now(UTC)
        self._updated_at = datetime.now(UTC)

    def update_preferences(
        self,
        *,
        preferred_wpm: PreferredWPM | None | object = _UNSET,
        preferred_words_per_flash: PreferredWordsPerFlash | None | object = _UNSET,
        skip_images: bool | object = _UNSET,
        ramp_up_enabled: bool | object = _UNSET,
    ) -> None:
        if preferred_wpm is not _UNSET:
            self._preferred_wpm = cast("PreferredWPM | None", preferred_wpm)
        if preferred_words_per_flash is not _UNSET:
            self._preferred_words_per_flash = cast(
                "PreferredWordsPerFlash | None",
                preferred_words_per_flash,
            )
        if skip_images is not _UNSET:
            self._skip_images = cast("bool", skip_images)
        if ramp_up_enabled is not _UNSET:
            self._ramp_up_enabled = cast("bool", ramp_up_enabled)
        self._updated_at = datetime.now(UTC)

    def _require_active(self, action: str) -> None:
        if self._access_status is not AccessStatus.ACTIVE:
            raise InvalidLibraryItemStateError(
                f"Cannot {action} a library item that is not active.",
            )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LibraryItem) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId
    from app.domain.user_book_state.value_objects import (
        PreferredWordsPerFlash,
        PreferredWPM,
    )


class UserBookState:
    def __init__(
        self,
        *,
        user_id: UserId,
        book_id: BookId,
        favorited_at: datetime | None = None,
        archived_at: datetime | None = None,
        completed_at: datetime | None = None,
        last_opened_at: datetime | None = None,
        preferred_wpm: PreferredWPM | None = None,
        preferred_words_per_flash: PreferredWordsPerFlash | None = None,
        skip_images: bool = False,
        ramp_up_enabled: bool = True,
    ) -> None:
        self._user_id = user_id
        self._book_id = book_id
        self._favorited_at = favorited_at
        self._archived_at = archived_at
        self._completed_at = completed_at
        self._last_opened_at = last_opened_at
        self._preferred_wpm = preferred_wpm
        self._preferred_words_per_flash = preferred_words_per_flash
        self._skip_images = skip_images
        self._ramp_up_enabled = ramp_up_enabled

    @classmethod
    def create(cls, *, user_id: UserId, book_id: BookId) -> UserBookState:
        return cls(user_id=user_id, book_id=book_id)

    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def book_id(self) -> BookId:
        return self._book_id

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

    def favorite(self, at: datetime | None = None) -> None:
        self._favorited_at = at or datetime.now(UTC)

    def unfavorite(self) -> None:
        self._favorited_at = None

    def archive(self, at: datetime | None = None) -> None:
        self._archived_at = at or datetime.now(UTC)

    def unarchive(self) -> None:
        self._archived_at = None

    def mark_completed(self, at: datetime | None = None) -> None:
        self._completed_at = at or datetime.now(UTC)

    def reopen(self) -> None:
        self._completed_at = None

    def record_opened(self, at: datetime | None = None) -> None:
        self._last_opened_at = at or datetime.now(UTC)

    def update_preferences(
        self,
        *,
        preferred_wpm: PreferredWPM | None = None,
        preferred_words_per_flash: PreferredWordsPerFlash | None = None,
        skip_images: bool | None = None,
        ramp_up_enabled: bool | None = None,
    ) -> None:
        self._preferred_wpm = preferred_wpm
        self._preferred_words_per_flash = preferred_words_per_flash
        if skip_images is not None:
            self._skip_images = skip_images
        if ramp_up_enabled is not None:
            self._ramp_up_enabled = ramp_up_enabled

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, UserBookState)
            and self._user_id == other._user_id
            and self._book_id == other._book_id
        )

    def __hash__(self) -> int:
        return hash((self._user_id, self._book_id))

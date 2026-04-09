from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.domain.reading_sessions.value_objects import (
    CurrentChunk,
    CurrentWordIndex,
    ReadingSessionId,
    WordsPerFlash,
    WpmSpeed,
)

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId


class ReadingSession:
    def __init__(
        self,
        *,
        id: ReadingSessionId,
        user_id: UserId,
        book_id: BookId,
        current_word_index: CurrentWordIndex,
        current_chunk: CurrentChunk,
        wpm_speed: WpmSpeed,
        words_per_flash: WordsPerFlash,
        last_read_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._book_id = book_id
        self._current_word_index = current_word_index
        self._current_chunk = current_chunk
        self._wpm_speed = wpm_speed
        self._words_per_flash = words_per_flash
        self._last_read_at = last_read_at or datetime.now(UTC)
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        user_id: UserId,
        book_id: BookId,
        wpm_speed: WpmSpeed | None = None,
        words_per_flash: WordsPerFlash | None = None,
    ) -> ReadingSession:
        return cls(
            id=ReadingSessionId.generate(),
            user_id=user_id,
            book_id=book_id,
            current_word_index=CurrentWordIndex(0),
            current_chunk=CurrentChunk(0),
            wpm_speed=wpm_speed or WpmSpeed(250),
            words_per_flash=words_per_flash or WordsPerFlash(1),
        )

    @property
    def id(self) -> ReadingSessionId:
        return self._id

    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def book_id(self) -> BookId:
        return self._book_id

    @property
    def current_word_index(self) -> CurrentWordIndex:
        return self._current_word_index

    @property
    def current_chunk(self) -> CurrentChunk:
        return self._current_chunk

    @property
    def wpm_speed(self) -> WpmSpeed:
        return self._wpm_speed

    @property
    def words_per_flash(self) -> WordsPerFlash:
        return self._words_per_flash

    @property
    def last_read_at(self) -> datetime:
        return self._last_read_at

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def update_progress(
        self,
        *,
        current_word_index: CurrentWordIndex,
        current_chunk: CurrentChunk,
        wpm_speed: WpmSpeed | None = None,
        words_per_flash: WordsPerFlash | None = None,
    ) -> None:
        now = datetime.now(UTC)
        self._current_word_index = current_word_index
        self._current_chunk = current_chunk
        if wpm_speed is not None:
            self._wpm_speed = wpm_speed
        if words_per_flash is not None:
            self._words_per_flash = words_per_flash
        self._last_read_at = now
        self._updated_at = now

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ReadingSession) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

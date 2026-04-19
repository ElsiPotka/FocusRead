from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

from app.domain.reading_stats.value_objects import (
    AverageWpm,
    ReadingStatId,
    SessionDate,
    TimeSpentSeconds,
    WordsRead,
)

if TYPE_CHECKING:
    from app.domain.library_item.value_objects import LibraryItemId


class ReadingStat:
    """Per-day reading activity for a single `LibraryItem`.

    Re-anchored from `(user_id, book_id)` to `library_item_id`. Unique per
    `(library_item_id, session_date)` at the DB layer.
    """

    def __init__(
        self,
        *,
        id: ReadingStatId,
        library_item_id: LibraryItemId,
        session_date: SessionDate,
        words_read: WordsRead,
        time_spent_sec: TimeSpentSeconds,
        avg_wpm: AverageWpm | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._library_item_id = library_item_id
        self._session_date = session_date
        self._words_read = words_read
        self._time_spent_sec = time_spent_sec
        self._avg_wpm = avg_wpm
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        library_item_id: LibraryItemId,
        session_date: SessionDate | None = None,
    ) -> ReadingStat:
        return cls(
            id=ReadingStatId.generate(),
            library_item_id=library_item_id,
            session_date=session_date or SessionDate(date.today()),
            words_read=WordsRead(0),
            time_spent_sec=TimeSpentSeconds(0),
        )

    @property
    def id(self) -> ReadingStatId:
        return self._id

    @property
    def library_item_id(self) -> LibraryItemId:
        return self._library_item_id

    @property
    def session_date(self) -> SessionDate:
        return self._session_date

    @property
    def words_read(self) -> WordsRead:
        return self._words_read

    @property
    def time_spent_sec(self) -> TimeSpentSeconds:
        return self._time_spent_sec

    @property
    def avg_wpm(self) -> AverageWpm | None:
        return self._avg_wpm

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def record_activity(
        self,
        *,
        words_read_delta: int,
        time_spent_delta_sec: int,
    ) -> None:
        new_words = self._words_read.value + words_read_delta
        new_time = self._time_spent_sec.value + time_spent_delta_sec
        self._words_read = WordsRead(new_words)
        self._time_spent_sec = TimeSpentSeconds(new_time)
        if new_time > 0:
            avg = round((new_words / new_time) * 60)
            self._avg_wpm = AverageWpm(avg) if avg > 0 else None
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ReadingStat) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003
from typing import TYPE_CHECKING

from app.domain.auth.value_objects import UserId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True, slots=True)
class DailyStat:
    date: date
    words_read: int
    time_spent_sec: int
    avg_wpm: int | None


@dataclass(frozen=True, slots=True)
class StatsSummary:
    total_words_read: int
    total_time_spent_sec: int
    books_read_count: int
    daily_stats: list[DailyStat]


class GetStatsSummary:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        user_id: UUID,
        since: date | None = None,
    ) -> StatsSummary:
        stats = await self._uow.reading_stats.list_for_user(
            user_id=UserId(user_id),
            since=since,
        )

        total_words = sum(s.words_read.value for s in stats)
        total_time = sum(s.time_spent_sec.value for s in stats)
        books_read = len(
            {s.library_item_id.value for s in stats if s.words_read.value > 0}
        )

        # Aggregate by date across all books
        daily: dict[date, tuple[int, int]] = {}
        for s in stats:
            d = s.session_date.value
            words, time = daily.get(d, (0, 0))
            daily[d] = (words + s.words_read.value, time + s.time_spent_sec.value)

        daily_stats = [
            DailyStat(
                date=d,
                words_read=words,
                time_spent_sec=time,
                avg_wpm=round((words / time) * 60) if time > 0 else None,
            )
            for d, (words, time) in sorted(daily.items(), reverse=True)
        ]

        return StatsSummary(
            total_words_read=total_words,
            total_time_spent_sec=total_time,
            books_read_count=books_read,
            daily_stats=daily_stats,
        )

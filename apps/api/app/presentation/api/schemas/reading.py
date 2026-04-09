from __future__ import annotations

from datetime import date, datetime  # noqa: TC003
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.application.reading.use_cases.get_stats_summary import (
        DailyStat,
        StatsSummary,
    )
    from app.domain.reading_sessions.entities import ReadingSession
    from app.domain.reading_stats.entities import ReadingStat


class ReadingSessionResponse(BaseModel):
    current_word_index: int
    current_chunk: int
    wpm_speed: int
    words_per_flash: int
    last_read_at: datetime

    @staticmethod
    def from_entity(session: ReadingSession) -> ReadingSessionResponse:
        return ReadingSessionResponse(
            current_word_index=session.current_word_index.value,
            current_chunk=session.current_chunk.value,
            wpm_speed=session.wpm_speed.value,
            words_per_flash=session.words_per_flash.value,
            last_read_at=session.last_read_at,
        )


class UpsertProgressRequest(BaseModel):
    current_word_index: int = Field(..., ge=0)
    current_chunk: int = Field(..., ge=0)
    wpm_speed: int | None = Field(None, ge=50, le=2000)
    words_per_flash: int | None = Field(None, ge=1, le=3)
    words_read_delta: int = Field(0, ge=0)
    time_spent_delta_sec: int = Field(0, ge=0)


class ReadingStatResponse(BaseModel):
    session_date: date
    words_read: int
    time_spent_sec: int
    avg_wpm: int | None

    @staticmethod
    def from_entity(stat: ReadingStat) -> ReadingStatResponse:
        return ReadingStatResponse(
            session_date=stat.session_date.value,
            words_read=stat.words_read.value,
            time_spent_sec=stat.time_spent_sec.value,
            avg_wpm=stat.avg_wpm.value if stat.avg_wpm else None,
        )


class DailyStatResponse(BaseModel):
    date: date
    words_read: int
    time_spent_sec: int
    avg_wpm: int | None

    @staticmethod
    def from_model(daily: DailyStat) -> DailyStatResponse:
        return DailyStatResponse(
            date=daily.date,
            words_read=daily.words_read,
            time_spent_sec=daily.time_spent_sec,
            avg_wpm=daily.avg_wpm,
        )


class StatsSummaryResponse(BaseModel):
    total_words_read: int
    total_time_spent_sec: int
    books_read_count: int
    daily_stats: list[DailyStatResponse]

    @staticmethod
    def from_model(summary: StatsSummary) -> StatsSummaryResponse:
        return StatsSummaryResponse(
            total_words_read=summary.total_words_read,
            total_time_spent_sec=summary.total_time_spent_sec,
            books_read_count=summary.books_read_count,
            daily_stats=[DailyStatResponse.from_model(d) for d in summary.daily_stats],
        )

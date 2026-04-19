from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from app.domain.library_item.value_objects import LibraryItemId
from app.domain.reading_stats.entities import ReadingStat

if TYPE_CHECKING:
    from app.domain.reading_stats.value_objects import SessionDate


def make_stat(
    *,
    library_item_id: LibraryItemId | None = None,
    session_date: SessionDate | None = None,
) -> ReadingStat:
    return ReadingStat.create(
        library_item_id=library_item_id or LibraryItemId(uuid4()),
        session_date=session_date,
    )


def test_create_defaults():
    stat = make_stat()
    assert stat.words_read.value == 0
    assert stat.time_spent_sec.value == 0
    assert stat.avg_wpm is None


def test_record_activity_accumulates():
    stat = make_stat()
    stat.record_activity(words_read_delta=500, time_spent_delta_sec=60)
    assert stat.words_read.value == 500
    assert stat.time_spent_sec.value == 60


def test_record_activity_twice_accumulates():
    stat = make_stat()
    stat.record_activity(words_read_delta=300, time_spent_delta_sec=30)
    stat.record_activity(words_read_delta=200, time_spent_delta_sec=30)
    assert stat.words_read.value == 500
    assert stat.time_spent_sec.value == 60


def test_record_activity_computes_avg_wpm():
    stat = make_stat()
    stat.record_activity(words_read_delta=600, time_spent_delta_sec=60)
    assert stat.avg_wpm is not None
    assert stat.avg_wpm.value == 600


def test_record_activity_no_avg_wpm_when_no_time():
    stat = make_stat()
    stat.record_activity(words_read_delta=100, time_spent_delta_sec=0)
    assert stat.avg_wpm is None


def test_equality_by_id():
    s1 = make_stat()
    s2 = make_stat()
    assert s1 != s2
    assert s1 == s1

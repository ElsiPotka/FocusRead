from __future__ import annotations

from uuid import uuid4

from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.reading_stats.entities import ReadingStat


def make_stat(**kwargs) -> ReadingStat:
    defaults = {
        "user_id": UserId(uuid4()),
        "book_id": BookId(uuid4()),
    }
    defaults.update(kwargs)
    return ReadingStat.create(**defaults)


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
    # 600 words in 60 seconds = 600 WPM
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

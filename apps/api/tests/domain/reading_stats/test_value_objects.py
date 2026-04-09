from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.domain.reading_stats.value_objects import (
    AverageWpm,
    SessionDate,
    TimeSpentSeconds,
    WordsRead,
)


def test_words_read_valid():
    assert WordsRead(0).value == 0
    assert WordsRead(5000).value == 5000


def test_words_read_negative_raises():
    with pytest.raises(ValueError, match="negative"):
        WordsRead(-1)


def test_time_spent_valid():
    assert TimeSpentSeconds(0).value == 0


def test_time_spent_negative_raises():
    with pytest.raises(ValueError, match="negative"):
        TimeSpentSeconds(-1)


def test_average_wpm_positive():
    assert AverageWpm(300).value == 300


def test_average_wpm_zero_or_negative_raises():
    with pytest.raises(ValueError, match="positive"):
        AverageWpm(0)
    with pytest.raises(ValueError, match="positive"):
        AverageWpm(-1)


def test_session_date_today():
    assert SessionDate(date.today()).value == date.today()


def test_session_date_past():
    yesterday = date.today() - timedelta(days=1)
    assert SessionDate(yesterday).value == yesterday


def test_session_date_future_raises():
    tomorrow = date.today() + timedelta(days=1)
    with pytest.raises(ValueError, match="future"):
        SessionDate(tomorrow)

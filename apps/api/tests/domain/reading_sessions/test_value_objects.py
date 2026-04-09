from __future__ import annotations

import pytest

from app.domain.reading_sessions.value_objects import (
    CurrentChunk,
    CurrentWordIndex,
    WordsPerFlash,
    WpmSpeed,
)


def test_current_word_index_valid():
    assert CurrentWordIndex(0).value == 0
    assert CurrentWordIndex(999).value == 999


def test_current_word_index_negative_raises():
    with pytest.raises(ValueError, match="negative"):
        CurrentWordIndex(-1)


def test_current_chunk_valid():
    assert CurrentChunk(0).value == 0


def test_current_chunk_negative_raises():
    with pytest.raises(ValueError, match="negative"):
        CurrentChunk(-1)


def test_wpm_speed_valid_range():
    assert WpmSpeed(50).value == 50
    assert WpmSpeed(250).value == 250
    assert WpmSpeed(2000).value == 2000


def test_wpm_speed_out_of_range_raises():
    with pytest.raises(ValueError, match="50 and 2000"):
        WpmSpeed(49)
    with pytest.raises(ValueError, match="50 and 2000"):
        WpmSpeed(2001)


def test_words_per_flash_valid():
    for v in (1, 2, 3):
        assert WordsPerFlash(v).value == v


def test_words_per_flash_invalid_raises():
    with pytest.raises(ValueError, match="1, 2, or 3"):
        WordsPerFlash(0)
    with pytest.raises(ValueError, match="1, 2, or 3"):
        WordsPerFlash(4)

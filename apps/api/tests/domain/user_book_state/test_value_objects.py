from __future__ import annotations

import pytest

from app.domain.user_book_state.value_objects import (
    PreferredWordsPerFlash,
    PreferredWPM,
)


def test_preferred_wpm_valid():
    assert PreferredWPM(1).value == 1
    assert PreferredWPM(250).value == 250
    assert PreferredWPM(2000).value == 2000


def test_preferred_wpm_zero_raises():
    with pytest.raises(ValueError, match="greater than zero"):
        PreferredWPM(0)


def test_preferred_wpm_negative_raises():
    with pytest.raises(ValueError, match="greater than zero"):
        PreferredWPM(-1)


def test_preferred_wpm_too_high_raises():
    with pytest.raises(ValueError, match="2000"):
        PreferredWPM(2001)


def test_preferred_words_per_flash_valid():
    for v in (1, 2, 3):
        assert PreferredWordsPerFlash(v).value == v


def test_preferred_words_per_flash_invalid_raises():
    with pytest.raises(ValueError, match="1, 2, or 3"):
        PreferredWordsPerFlash(0)
    with pytest.raises(ValueError, match="1, 2, or 3"):
        PreferredWordsPerFlash(4)

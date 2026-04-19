from __future__ import annotations

import pytest

from app.domain.library_item.value_objects import (
    LibrarySourceRef,
    PreferredWordsPerFlash,
    PreferredWPM,
    RevocationReason,
)


class TestLibrarySourceRef:
    def test_strips(self):
        assert LibrarySourceRef("  purchase:abc ").value == "purchase:abc"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Library source ref"):
            LibrarySourceRef("   ")

    def test_rejects_too_long(self):
        with pytest.raises(ValueError, match="Library source ref"):
            LibrarySourceRef("x" * 256)


class TestRevocationReason:
    def test_strips(self):
        assert RevocationReason("  chargeback ").value == "chargeback"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Revocation reason"):
            RevocationReason("   ")

    def test_rejects_too_long(self):
        with pytest.raises(ValueError, match="Revocation reason"):
            RevocationReason("x" * 5001)


class TestPreferredWPM:
    @pytest.mark.parametrize("value", [50, 300, 2000])
    def test_accepts_in_range(self, value: int):
        assert PreferredWPM(value).value == value

    @pytest.mark.parametrize("value", [49, 0, -1, 2001])
    def test_rejects_out_of_range(self, value: int):
        with pytest.raises(ValueError, match="Preferred WPM"):
            PreferredWPM(value)


class TestPreferredWordsPerFlash:
    @pytest.mark.parametrize("value", [1, 2, 3])
    def test_accepts_allowed(self, value: int):
        assert PreferredWordsPerFlash(value).value == value

    @pytest.mark.parametrize("value", [0, 4, -1])
    def test_rejects_other(self, value: int):
        with pytest.raises(ValueError, match="Preferred words per flash"):
            PreferredWordsPerFlash(value)

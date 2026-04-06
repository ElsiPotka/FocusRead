from __future__ import annotations

import pytest

from app.domain.books.value_objects import (
    BookPageCount,
    BookSourceFilename,
    BookSubtitle,
)


class TestBookSubtitle:
    def test_strips_whitespace(self):
        assert BookSubtitle("  Clean Code  ").value == "Clean Code"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="cannot be blank"):
            BookSubtitle("   ")


class TestBookSourceFilename:
    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="cannot be blank"):
            BookSourceFilename("")


class TestBookPageCount:
    def test_requires_positive_value(self):
        with pytest.raises(ValueError, match="greater than zero"):
            BookPageCount(0)

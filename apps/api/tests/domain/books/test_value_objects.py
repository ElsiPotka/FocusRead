from __future__ import annotations

import pytest

from app.domain.books.value_objects import (
    BookCoverImagePath,
    BookDescription,
    BookDocumentType,
    BookLanguage,
    BookPublishedYear,
    BookPublisher,
    BookSubtitle,
    BookTitle,
)


class TestBookTitle:
    def test_strips_whitespace(self):
        assert BookTitle("  Deep Work  ").value == "Deep Work"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Book title"):
            BookTitle("   ")

    def test_rejects_too_long(self):
        with pytest.raises(ValueError, match="Book title"):
            BookTitle("x" * 501)


class TestBookSubtitle:
    def test_strips_whitespace(self):
        assert BookSubtitle("  Clean Code  ").value == "Clean Code"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="cannot be blank"):
            BookSubtitle("   ")


class TestBookDescription:
    def test_strips_whitespace(self):
        assert BookDescription("  a desc  ").value == "a desc"

    def test_rejects_too_long(self):
        with pytest.raises(ValueError, match="Book description"):
            BookDescription("x" * 5001)


class TestBookLanguage:
    def test_normalizes_lowercase(self):
        assert BookLanguage("EN").value == "en"

    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Book language"):
            BookLanguage("  ")


class TestBookPublisher:
    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Book publisher"):
            BookPublisher("   ")


class TestBookPublishedYear:
    @pytest.mark.parametrize("value", [1, 2024, 9999])
    def test_accepts_in_range(self, value: int):
        assert BookPublishedYear(value).value == value

    @pytest.mark.parametrize("value", [0, -1, 10000])
    def test_rejects_out_of_range(self, value: int):
        with pytest.raises(ValueError, match="Book published year"):
            BookPublishedYear(value)


class TestBookCoverImagePath:
    def test_rejects_blank(self):
        with pytest.raises(ValueError, match="Book cover image path"):
            BookCoverImagePath("   ")


class TestBookDocumentType:
    @pytest.mark.parametrize("raw", ["book", "article", "paper", "manual", "other"])
    def test_accepts_known_kinds(self, raw: str):
        assert BookDocumentType(raw).value == raw

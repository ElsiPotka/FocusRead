from __future__ import annotations

import pytest

from app.domain.book_toc_entry.value_objects import BookTOCEntryId, BookTOCTitle


def test_toc_entry_id_generate():
    id1 = BookTOCEntryId.generate()
    id2 = BookTOCEntryId.generate()
    assert id1 != id2
    assert str(id1) == str(id1.value)


def test_toc_title_valid():
    title = BookTOCTitle("Chapter 1: Introduction")
    assert title.value == "Chapter 1: Introduction"


def test_toc_title_strips_whitespace():
    title = BookTOCTitle("  Chapter 1  ")
    assert title.value == "Chapter 1"


def test_toc_title_rejects_empty():
    with pytest.raises(ValueError, match="title is required"):
        BookTOCTitle("")


def test_toc_title_rejects_blank():
    with pytest.raises(ValueError, match="title is required"):
        BookTOCTitle("   ")


def test_toc_title_rejects_too_long():
    with pytest.raises(ValueError, match="500 characters"):
        BookTOCTitle("x" * 501)


def test_toc_title_accepts_max_length():
    title = BookTOCTitle("x" * 500)
    assert len(title.value) == 500

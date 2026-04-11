from __future__ import annotations

import pytest

from app.domain.bookmark.value_objects import BookmarkId, BookmarkLabel, BookmarkNote


def test_bookmark_id_generate():
    id1 = BookmarkId.generate()
    id2 = BookmarkId.generate()
    assert id1 != id2
    assert str(id1) == str(id1.value)


def test_bookmark_label_valid():
    label = BookmarkLabel("Important")
    assert label.value == "Important"


def test_bookmark_label_strips_whitespace():
    label = BookmarkLabel("  Important  ")
    assert label.value == "Important"


def test_bookmark_label_rejects_empty():
    with pytest.raises(ValueError, match="cannot be blank"):
        BookmarkLabel("")


def test_bookmark_label_rejects_blank():
    with pytest.raises(ValueError, match="cannot be blank"):
        BookmarkLabel("   ")


def test_bookmark_label_rejects_too_long():
    with pytest.raises(ValueError, match="255 characters"):
        BookmarkLabel("x" * 256)


def test_bookmark_note_valid():
    note = BookmarkNote("This is a note")
    assert note.value == "This is a note"


def test_bookmark_note_strips_whitespace():
    note = BookmarkNote("  Note  ")
    assert note.value == "Note"


def test_bookmark_note_rejects_empty():
    with pytest.raises(ValueError, match="cannot be blank"):
        BookmarkNote("")


def test_bookmark_note_rejects_too_long():
    with pytest.raises(ValueError, match="5000 characters"):
        BookmarkNote("x" * 5001)

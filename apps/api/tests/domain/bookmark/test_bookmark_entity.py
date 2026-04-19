from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.bookmark.entities import Bookmark
from app.domain.bookmark.value_objects import BookmarkLabel, BookmarkNote
from app.domain.library_item.value_objects import LibraryItemId


@pytest.fixture
def library_item_id() -> LibraryItemId:
    return LibraryItemId(uuid4())


def test_create_minimal(library_item_id):
    bookmark = Bookmark.create(
        library_item_id=library_item_id,
        word_index=100,
    )
    assert bookmark.library_item_id == library_item_id
    assert bookmark.word_index == 100
    assert bookmark.chunk_index is None
    assert bookmark.page_number is None
    assert bookmark.label is None
    assert bookmark.note is None


def test_create_with_all_fields(library_item_id):
    bookmark = Bookmark.create(
        library_item_id=library_item_id,
        word_index=500,
        chunk_index=2,
        page_number=15,
        label=BookmarkLabel("Important"),
        note=BookmarkNote("Remember this passage"),
    )
    assert bookmark.word_index == 500
    assert bookmark.chunk_index == 2
    assert bookmark.page_number == 15
    assert bookmark.label is not None
    assert bookmark.note is not None
    assert bookmark.label.value == "Important"
    assert bookmark.note.value == "Remember this passage"


def test_create_rejects_negative_word_index(library_item_id):
    with pytest.raises(ValueError, match="word index cannot be negative"):
        Bookmark.create(library_item_id=library_item_id, word_index=-1)


def test_create_rejects_negative_chunk_index(library_item_id):
    with pytest.raises(ValueError, match="chunk index cannot be negative"):
        Bookmark.create(library_item_id=library_item_id, word_index=0, chunk_index=-1)


def test_create_rejects_zero_page_number(library_item_id):
    with pytest.raises(ValueError, match="page number must be positive"):
        Bookmark.create(library_item_id=library_item_id, word_index=0, page_number=0)


def test_move_to(library_item_id):
    bookmark = Bookmark.create(library_item_id=library_item_id, word_index=0)
    old_updated = bookmark.updated_at

    bookmark.move_to(word_index=200, chunk_index=1, page_number=5)

    assert bookmark.word_index == 200
    assert bookmark.chunk_index == 1
    assert bookmark.page_number == 5
    assert bookmark.updated_at >= old_updated


def test_move_to_rejects_negative_word_index(library_item_id):
    bookmark = Bookmark.create(library_item_id=library_item_id, word_index=0)
    with pytest.raises(ValueError, match="word index cannot be negative"):
        bookmark.move_to(word_index=-1)


def test_annotate(library_item_id):
    bookmark = Bookmark.create(library_item_id=library_item_id, word_index=0)
    bookmark.annotate(
        label=BookmarkLabel("Highlight"),
        note=BookmarkNote("Key insight"),
    )
    assert bookmark.label is not None
    assert bookmark.note is not None
    assert bookmark.label.value == "Highlight"
    assert bookmark.note.value == "Key insight"


def test_annotate_clears_fields(library_item_id):
    bookmark = Bookmark.create(
        library_item_id=library_item_id,
        word_index=0,
        label=BookmarkLabel("Old"),
        note=BookmarkNote("Old note"),
    )
    bookmark.annotate(label=None, note=None)
    assert bookmark.label is None
    assert bookmark.note is None


def test_equality(library_item_id):
    bookmark = Bookmark.create(library_item_id=library_item_id, word_index=0)
    same = Bookmark(
        id=bookmark.id,
        library_item_id=library_item_id,
        word_index=999,
    )
    assert bookmark == same
    assert hash(bookmark) == hash(same)

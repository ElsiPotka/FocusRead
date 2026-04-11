from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.auth.value_objects import UserId
from app.domain.bookmark.entities import Bookmark
from app.domain.bookmark.value_objects import BookmarkLabel, BookmarkNote
from app.domain.books.value_objects import BookId


@pytest.fixture
def user_id() -> UserId:
    return UserId(uuid4())


@pytest.fixture
def book_id() -> BookId:
    return BookId(uuid4())


def test_create_minimal(user_id, book_id):
    bookmark = Bookmark.create(
        user_id=user_id,
        book_id=book_id,
        word_index=100,
    )
    assert bookmark.word_index == 100
    assert bookmark.chunk_index is None
    assert bookmark.page_number is None
    assert bookmark.label is None
    assert bookmark.note is None


def test_create_with_all_fields(user_id, book_id):
    bookmark = Bookmark.create(
        user_id=user_id,
        book_id=book_id,
        word_index=500,
        chunk_index=2,
        page_number=15,
        label=BookmarkLabel("Important"),
        note=BookmarkNote("Remember this passage"),
    )
    assert bookmark.word_index == 500
    assert bookmark.chunk_index == 2
    assert bookmark.page_number == 15
    assert bookmark.label.value == "Important"
    assert bookmark.note.value == "Remember this passage"


def test_create_rejects_negative_word_index(user_id, book_id):
    with pytest.raises(ValueError, match="word index cannot be negative"):
        Bookmark.create(user_id=user_id, book_id=book_id, word_index=-1)


def test_create_rejects_negative_chunk_index(user_id, book_id):
    with pytest.raises(ValueError, match="chunk index cannot be negative"):
        Bookmark.create(user_id=user_id, book_id=book_id, word_index=0, chunk_index=-1)


def test_create_rejects_zero_page_number(user_id, book_id):
    with pytest.raises(ValueError, match="page number must be positive"):
        Bookmark.create(user_id=user_id, book_id=book_id, word_index=0, page_number=0)


def test_move_to(user_id, book_id):
    bookmark = Bookmark.create(
        user_id=user_id, book_id=book_id, word_index=0
    )
    old_updated = bookmark.updated_at

    bookmark.move_to(word_index=200, chunk_index=1, page_number=5)

    assert bookmark.word_index == 200
    assert bookmark.chunk_index == 1
    assert bookmark.page_number == 5
    assert bookmark.updated_at >= old_updated


def test_move_to_rejects_negative_word_index(user_id, book_id):
    bookmark = Bookmark.create(
        user_id=user_id, book_id=book_id, word_index=0
    )
    with pytest.raises(ValueError, match="word index cannot be negative"):
        bookmark.move_to(word_index=-1)


def test_annotate(user_id, book_id):
    bookmark = Bookmark.create(
        user_id=user_id, book_id=book_id, word_index=0
    )
    bookmark.annotate(
        label=BookmarkLabel("Highlight"),
        note=BookmarkNote("Key insight"),
    )
    assert bookmark.label.value == "Highlight"
    assert bookmark.note.value == "Key insight"


def test_annotate_clears_fields(user_id, book_id):
    bookmark = Bookmark.create(
        user_id=user_id,
        book_id=book_id,
        word_index=0,
        label=BookmarkLabel("Old"),
        note=BookmarkNote("Old note"),
    )
    bookmark.annotate(label=None, note=None)
    assert bookmark.label is None
    assert bookmark.note is None


def test_equality(user_id, book_id):
    bookmark = Bookmark.create(
        user_id=user_id, book_id=book_id, word_index=0
    )
    same = Bookmark(
        id=bookmark.id,
        user_id=user_id,
        book_id=book_id,
        word_index=999,
    )
    assert bookmark == same
    assert hash(bookmark) == hash(same)

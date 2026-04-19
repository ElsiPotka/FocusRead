from __future__ import annotations

from uuid import uuid4

import pytest

from app.domain.book_asset.value_objects import BookAssetId
from app.domain.book_toc_entry.entities import BookTOCEntry
from app.domain.book_toc_entry.value_objects import BookTOCEntryId, BookTOCTitle


@pytest.fixture
def book_asset_id() -> BookAssetId:
    return BookAssetId(uuid4())


def test_create_entry(book_asset_id):
    entry = BookTOCEntry.create(
        book_asset_id=book_asset_id,
        title=BookTOCTitle("Chapter 1"),
        level=1,
        order_index=0,
    )
    assert entry.title.value == "Chapter 1"
    assert entry.level == 1
    assert entry.order_index == 0
    assert entry.parent_id is None
    assert entry.page_start is None
    assert entry.start_word_index is None


def test_create_entry_with_all_fields(book_asset_id):
    parent_id = BookTOCEntryId.generate()
    entry = BookTOCEntry.create(
        book_asset_id=book_asset_id,
        title=BookTOCTitle("Section 1.1"),
        level=2,
        order_index=1,
        parent_id=parent_id,
        page_start=5,
        start_word_index=1000,
    )
    assert entry.level == 2
    assert entry.parent_id == parent_id
    assert entry.page_start == 5
    assert entry.start_word_index == 1000


def test_create_rejects_zero_level(book_asset_id):
    with pytest.raises(ValueError, match="level must be positive"):
        BookTOCEntry.create(
            book_asset_id=book_asset_id,
            title=BookTOCTitle("Bad"),
            level=0,
            order_index=0,
        )


def test_create_rejects_negative_order_index(book_asset_id):
    with pytest.raises(ValueError, match="order index cannot be negative"):
        BookTOCEntry.create(
            book_asset_id=book_asset_id,
            title=BookTOCTitle("Bad"),
            level=1,
            order_index=-1,
        )


def test_create_rejects_zero_page_start(book_asset_id):
    with pytest.raises(ValueError, match="page start must be positive"):
        BookTOCEntry.create(
            book_asset_id=book_asset_id,
            title=BookTOCTitle("Bad"),
            level=1,
            order_index=0,
            page_start=0,
        )


def test_create_rejects_negative_start_word_index(book_asset_id):
    with pytest.raises(ValueError, match="start word index cannot be negative"):
        BookTOCEntry.create(
            book_asset_id=book_asset_id,
            title=BookTOCTitle("Bad"),
            level=1,
            order_index=0,
            start_word_index=-1,
        )


def test_reposition(book_asset_id):
    entry = BookTOCEntry.create(
        book_asset_id=book_asset_id,
        title=BookTOCTitle("Chapter 1"),
        level=1,
        order_index=0,
    )
    old_updated = entry.updated_at

    parent_id = BookTOCEntryId.generate()
    entry.reposition(level=2, order_index=3, parent_id=parent_id, page_start=10)

    assert entry.level == 2
    assert entry.order_index == 3
    assert entry.parent_id == parent_id
    assert entry.page_start == 10
    assert entry.updated_at >= old_updated


def test_rename(book_asset_id):
    entry = BookTOCEntry.create(
        book_asset_id=book_asset_id,
        title=BookTOCTitle("Old Title"),
        level=1,
        order_index=0,
    )
    entry.rename(BookTOCTitle("New Title"))
    assert entry.title.value == "New Title"


def test_equality(book_asset_id):
    entry = BookTOCEntry.create(
        book_asset_id=book_asset_id,
        title=BookTOCTitle("Chapter 1"),
        level=1,
        order_index=0,
    )
    same = BookTOCEntry(
        id=entry.id,
        book_asset_id=book_asset_id,
        title=BookTOCTitle("Different"),
        level=1,
        order_index=0,
    )
    assert entry == same
    assert hash(entry) == hash(same)

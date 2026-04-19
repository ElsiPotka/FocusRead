from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.bookmarks.use_cases.update_bookmark import (
    BookmarkUpdate,
    UpdateBookmark,
)
from app.application.common.errors import NotFoundError
from app.domain.bookmark.entities import Bookmark
from app.domain.bookmark.value_objects import BookmarkLabel, BookmarkNote


async def test_update_bookmark_move(
    uow, bookmark_repo, library_item_repo, library_item
):
    bookmark = Bookmark.create(
        library_item_id=library_item.id,
        word_index=100,
    )
    bookmark_repo.get.return_value = bookmark
    library_item_repo.get.return_value = library_item

    result = await UpdateBookmark(uow).execute(
        bookmark_id=bookmark.id.value,
        user_id=library_item.user_id.value,
        update=BookmarkUpdate(word_index=500, chunk_index=3, page_number=10),
    )

    assert result.word_index == 500
    assert result.chunk_index == 3
    assert result.page_number == 10
    bookmark_repo.save.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_update_bookmark_annotate(
    uow, bookmark_repo, library_item_repo, library_item
):
    bookmark = Bookmark.create(
        library_item_id=library_item.id,
        word_index=100,
    )
    bookmark_repo.get.return_value = bookmark
    library_item_repo.get.return_value = library_item

    result = await UpdateBookmark(uow).execute(
        bookmark_id=bookmark.id.value,
        user_id=library_item.user_id.value,
        update=BookmarkUpdate(label="Highlight", note="Key point"),
    )

    assert result.label is not None
    assert result.note is not None
    assert result.label.value == "Highlight"
    assert result.note.value == "Key point"


async def test_update_bookmark_clear_label(
    uow, bookmark_repo, library_item_repo, library_item
):
    bookmark = Bookmark.create(
        library_item_id=library_item.id,
        word_index=100,
        label=BookmarkLabel("Old"),
    )
    bookmark_repo.get.return_value = bookmark
    library_item_repo.get.return_value = library_item

    result = await UpdateBookmark(uow).execute(
        bookmark_id=bookmark.id.value,
        user_id=library_item.user_id.value,
        update=BookmarkUpdate(clear_label=True),
    )

    assert result.label is None


async def test_update_bookmark_clear_note(
    uow, bookmark_repo, library_item_repo, library_item
):
    bookmark = Bookmark.create(
        library_item_id=library_item.id,
        word_index=100,
        note=BookmarkNote("Old note"),
    )
    bookmark_repo.get.return_value = bookmark
    library_item_repo.get.return_value = library_item

    result = await UpdateBookmark(uow).execute(
        bookmark_id=bookmark.id.value,
        user_id=library_item.user_id.value,
        update=BookmarkUpdate(clear_note=True),
    )

    assert result.note is None


async def test_update_bookmark_not_found(uow, bookmark_repo):
    bookmark_repo.get.return_value = None

    with pytest.raises(NotFoundError, match="Bookmark not found"):
        await UpdateBookmark(uow).execute(
            bookmark_id=uuid4(),
            user_id=uuid4(),
            update=BookmarkUpdate(word_index=0),
        )

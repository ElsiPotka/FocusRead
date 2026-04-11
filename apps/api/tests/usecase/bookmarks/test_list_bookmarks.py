from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.bookmarks.use_cases.list_bookmarks import ListBookmarks
from app.application.common.errors import NotFoundError
from app.domain.bookmark.entities import Bookmark


async def test_list_bookmarks_returns_entries(uow, book_repo, bookmark_repo, book):
    bookmarks = [
        Bookmark.create(
            user_id=book.owner_user_id,
            book_id=book.id,
            word_index=100,
        ),
        Bookmark.create(
            user_id=book.owner_user_id,
            book_id=book.id,
            word_index=500,
        ),
    ]
    book_repo.get_for_owner.return_value = book
    bookmark_repo.list_for_book.return_value = bookmarks

    result = await ListBookmarks(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
    )

    assert len(result) == 2
    bookmark_repo.list_for_book.assert_awaited_once()


async def test_list_bookmarks_empty(uow, book_repo, bookmark_repo, book):
    book_repo.get_for_owner.return_value = book
    bookmark_repo.list_for_book.return_value = []

    result = await ListBookmarks(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
    )

    assert result == []


async def test_list_bookmarks_book_not_found(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await ListBookmarks(uow).execute(
            book_id=uuid4(),
            user_id=uuid4(),
        )

from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.bookmarks.use_cases.delete_bookmark import DeleteBookmark
from app.application.common.errors import NotFoundError
from app.domain.bookmark.entities import Bookmark


async def test_delete_bookmark(uow, bookmark_repo, book):
    bookmark = Bookmark.create(
        user_id=book.owner_user_id,
        book_id=book.id,
        word_index=100,
    )
    bookmark_repo.get_for_owner.return_value = bookmark

    await DeleteBookmark(uow).execute(
        bookmark_id=bookmark.id.value,
        user_id=book.owner_user_id.value,
    )

    bookmark_repo.delete.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_delete_bookmark_not_found(uow, bookmark_repo):
    bookmark_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Bookmark not found"):
        await DeleteBookmark(uow).execute(
            bookmark_id=uuid4(),
            user_id=uuid4(),
        )

from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.bookmarks.use_cases.delete_bookmark import DeleteBookmark
from app.application.common.errors import NotFoundError
from app.domain.bookmark.entities import Bookmark


async def test_delete_bookmark(uow, bookmark_repo, library_item_repo, library_item):
    bookmark = Bookmark.create(
        library_item_id=library_item.id,
        word_index=100,
    )
    bookmark_repo.get.return_value = bookmark
    library_item_repo.get.return_value = library_item

    await DeleteBookmark(uow).execute(
        bookmark_id=bookmark.id.value,
        user_id=library_item.user_id.value,
    )

    bookmark_repo.delete.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_delete_bookmark_not_found(uow, bookmark_repo):
    bookmark_repo.get.return_value = None

    with pytest.raises(NotFoundError, match="Bookmark not found"):
        await DeleteBookmark(uow).execute(
            bookmark_id=uuid4(),
            user_id=uuid4(),
        )

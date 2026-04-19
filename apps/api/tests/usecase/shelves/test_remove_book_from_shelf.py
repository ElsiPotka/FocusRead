from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.shelves import RemoveBookFromShelf


async def test_remove_book_from_shelf(
    uow, user_id, shelf, library_item, shelf_repo, library_item_repo
):
    shelf_repo.get_for_owner.return_value = shelf
    library_item_repo.get_active_for_user_book.return_value = library_item

    use_case = RemoveBookFromShelf(uow)
    await use_case.execute(
        shelf_id=shelf.id.value,
        book_id=library_item.book_id.value,
        user_id=user_id.value,
    )

    shelf_repo.remove_library_item.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_remove_book_shelf_not_found(uow, shelf_repo):
    shelf_repo.get_for_owner.return_value = None

    use_case = RemoveBookFromShelf(uow)
    with pytest.raises(NotFoundError, match="Shelf not found"):
        await use_case.execute(shelf_id=uuid4(), book_id=uuid4(), user_id=uuid4())

from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.shelves import AddBookToShelf


async def test_add_book_to_shelf(uow, user_id, shelf, book, shelf_repo, book_repo):
    shelf_repo.get_for_owner.return_value = shelf
    book_repo.get_for_owner.return_value = book
    shelf_repo.list_book_ids.return_value = []

    use_case = AddBookToShelf(uow)
    await use_case.execute(
        shelf_id=shelf.id.value,
        book_id=book.id.value,
        user_id=user_id.value,
    )

    shelf_repo.add_book.assert_awaited_once()
    call_kwargs = shelf_repo.add_book.call_args.kwargs
    assert call_kwargs["sort_order"] == 0
    uow.commit.assert_awaited_once()


async def test_add_book_auto_increments_order(uow, user_id, shelf, book, shelf_repo, book_repo):
    shelf_repo.get_for_owner.return_value = shelf
    book_repo.get_for_owner.return_value = book
    shelf_repo.list_book_ids.return_value = [uuid4(), uuid4()]

    use_case = AddBookToShelf(uow)
    await use_case.execute(
        shelf_id=shelf.id.value,
        book_id=book.id.value,
        user_id=user_id.value,
    )

    call_kwargs = shelf_repo.add_book.call_args.kwargs
    assert call_kwargs["sort_order"] == 2


async def test_add_book_shelf_not_found(uow, shelf_repo):
    shelf_repo.get_for_owner.return_value = None

    use_case = AddBookToShelf(uow)
    with pytest.raises(NotFoundError, match="Shelf not found"):
        await use_case.execute(
            shelf_id=uuid4(), book_id=uuid4(), user_id=uuid4()
        )


async def test_add_book_book_not_found(uow, user_id, shelf, shelf_repo, book_repo):
    shelf_repo.get_for_owner.return_value = shelf
    book_repo.get_for_owner.return_value = None

    use_case = AddBookToShelf(uow)
    with pytest.raises(NotFoundError, match="Book not found"):
        await use_case.execute(
            shelf_id=shelf.id.value, book_id=uuid4(), user_id=user_id.value
        )

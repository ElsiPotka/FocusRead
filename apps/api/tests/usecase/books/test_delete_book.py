from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.books.use_cases.delete_book import DeleteBook
from app.application.common.errors import NotFoundError


async def test_delete_book_removes_owned_book(
    uow, book_repo, book, book_id, owner_user_id
):
    book_repo.get_for_owner.return_value = book

    await DeleteBook(uow).execute(book_id=book_id, owner_user_id=owner_user_id)

    book_repo.delete.assert_awaited_once_with(book_id=book.id)
    uow.commit.assert_awaited_once()


async def test_delete_book_raises_when_missing(uow, book_repo, owner_user_id):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await DeleteBook(uow).execute(book_id=uuid4(), owner_user_id=owner_user_id)

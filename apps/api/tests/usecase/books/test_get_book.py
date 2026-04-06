from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.books.use_cases.get_book import GetBook
from app.application.common.errors import NotFoundError


async def test_get_book_returns_owned_book(
    uow, book_repo, book, book_id, owner_user_id
):
    book_repo.get_for_owner.return_value = book

    result = await GetBook(uow).execute(book_id=book_id, owner_user_id=owner_user_id)

    assert result == book
    book_repo.get_for_owner.assert_awaited_once()


async def test_get_book_raises_when_missing(uow, book_repo, owner_user_id):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await GetBook(uow).execute(book_id=uuid4(), owner_user_id=owner_user_id)

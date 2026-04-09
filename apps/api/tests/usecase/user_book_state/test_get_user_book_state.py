from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.user_book_state.use_cases.get_user_book_state import (
    GetUserBookState,
)
from app.domain.user_book_state.entities import UserBookState


async def test_returns_existing_state(uow, book_repo, state_repo, book):
    state = UserBookState.create(user_id=book.owner_user_id, book_id=book.id)
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = state

    result = await GetUserBookState(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
    )

    assert result == state


async def test_returns_none_when_no_state(uow, book_repo, state_repo, book):
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = None

    result = await GetUserBookState(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
    )

    assert result is None


async def test_book_not_found_raises(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await GetUserBookState(uow).execute(
            book_id=uuid4(),
            user_id=uuid4(),
        )

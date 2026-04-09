from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.user_book_state.use_cases.toggle_completed import ToggleCompleted
from app.domain.user_book_state.entities import UserBookState


async def test_complete_creates_state(uow, book_repo, state_repo, book):
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = None

    result = await ToggleCompleted(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        action="complete",
    )

    assert result.completed_at is not None
    state_repo.save.assert_awaited_once()


async def test_reopen(uow, book_repo, state_repo, book):
    existing = UserBookState.create(user_id=book.owner_user_id, book_id=book.id)
    existing.mark_completed()
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = existing

    result = await ToggleCompleted(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        action="reopen",
    )

    assert result.completed_at is None


async def test_book_not_found_raises(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await ToggleCompleted(uow).execute(
            book_id=uuid4(),
            user_id=uuid4(),
            action="complete",
        )

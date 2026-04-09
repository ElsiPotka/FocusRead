from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.user_book_state.use_cases.toggle_archive import ToggleArchive
from app.domain.user_book_state.entities import UserBookState


async def test_archive_creates_state(uow, book_repo, state_repo, book):
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = None

    result = await ToggleArchive(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        action="archive",
    )

    assert result.archived_at is not None
    state_repo.save.assert_awaited_once()


async def test_unarchive(uow, book_repo, state_repo, book):
    existing = UserBookState.create(user_id=book.owner_user_id, book_id=book.id)
    existing.archive()
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = existing

    result = await ToggleArchive(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        action="unarchive",
    )

    assert result.archived_at is None


async def test_book_not_found_raises(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await ToggleArchive(uow).execute(
            book_id=uuid4(),
            user_id=uuid4(),
            action="archive",
        )

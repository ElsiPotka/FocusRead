from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.user_book_state.use_cases.toggle_favorite import ToggleFavorite
from app.domain.user_book_state.entities import UserBookState


async def test_favorite_creates_state_when_none(uow, book_repo, state_repo, book):
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = None

    result = await ToggleFavorite(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        action="favorite",
    )

    assert result.favorited_at is not None
    state_repo.save.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_favorite_existing_state(uow, book_repo, state_repo, book):
    existing = UserBookState.create(user_id=book.owner_user_id, book_id=book.id)
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = existing

    result = await ToggleFavorite(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        action="favorite",
    )

    assert result.favorited_at is not None


async def test_unfavorite(uow, book_repo, state_repo, book):
    existing = UserBookState.create(user_id=book.owner_user_id, book_id=book.id)
    existing.favorite()
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = existing

    result = await ToggleFavorite(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        action="unfavorite",
    )

    assert result.favorited_at is None


async def test_book_not_found_raises(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await ToggleFavorite(uow).execute(
            book_id=uuid4(),
            user_id=uuid4(),
            action="favorite",
        )

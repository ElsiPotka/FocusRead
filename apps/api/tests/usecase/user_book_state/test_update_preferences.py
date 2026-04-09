from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.common.errors import NotFoundError
from app.application.user_book_state.use_cases.update_preferences import (
    PreferencesUpdate,
    UpdatePreferences,
)
from app.domain.user_book_state.entities import UserBookState


async def test_creates_state_with_preferences(uow, book_repo, state_repo, book):
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = None

    result = await UpdatePreferences(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        update=PreferencesUpdate(preferred_wpm=400, skip_images=True),
    )

    assert result.preferred_wpm is not None and result.preferred_wpm.value == 400
    assert result.skip_images is True
    state_repo.save.assert_awaited_once()
    uow.commit.assert_awaited_once()


async def test_updates_existing_state(uow, book_repo, state_repo, book):
    existing = UserBookState.create(user_id=book.owner_user_id, book_id=book.id)
    book_repo.get_for_owner.return_value = book
    state_repo.get.return_value = existing

    result = await UpdatePreferences(uow).execute(
        book_id=book.id.value,
        user_id=book.owner_user_id.value,
        update=PreferencesUpdate(ramp_up_enabled=False),
    )

    assert result.ramp_up_enabled is False


async def test_book_not_found_raises(uow, book_repo):
    book_repo.get_for_owner.return_value = None

    with pytest.raises(NotFoundError, match="Book not found"):
        await UpdatePreferences(uow).execute(
            book_id=uuid4(),
            user_id=uuid4(),
            update=PreferencesUpdate(),
        )

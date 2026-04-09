from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.user_book_state.entities import UserBookState
from app.domain.user_book_state.value_objects import (
    PreferredWordsPerFlash,
    PreferredWPM,
)

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True, slots=True)
class PreferencesUpdate:
    preferred_wpm: int | None = None
    preferred_words_per_flash: int | None = None
    skip_images: bool | None = None
    ramp_up_enabled: bool | None = None


class UpdatePreferences:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        book_id: UUID,
        user_id: UUID,
        update: PreferencesUpdate,
    ) -> UserBookState:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        state = await self._uow.user_book_states.get(
            user_id=UserId(user_id),
            book_id=BookId(book_id),
        )
        if state is None:
            state = UserBookState.create(
                user_id=UserId(user_id),
                book_id=BookId(book_id),
            )

        state.update_preferences(
            preferred_wpm=(
                PreferredWPM(update.preferred_wpm) if update.preferred_wpm else None
            ),
            preferred_words_per_flash=(
                PreferredWordsPerFlash(update.preferred_words_per_flash)
                if update.preferred_words_per_flash
                else None
            ),
            skip_images=update.skip_images,
            ramp_up_enabled=update.ramp_up_enabled,
        )
        await self._uow.user_book_states.save(state)
        await self._uow.commit()
        return state

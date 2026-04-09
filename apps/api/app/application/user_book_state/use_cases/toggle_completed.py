from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.user_book_state.entities import UserBookState

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class ToggleCompleted:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        book_id: UUID,
        user_id: UUID,
        action: str,
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

        if action == "complete":
            state.mark_completed()
        else:
            state.reopen()

        await self._uow.user_book_states.save(state)
        await self._uow.commit()
        return state

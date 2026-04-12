from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.value_objects import UserId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.books.entities import Book


class GetUserBooks:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, user_id: UUID) -> list[Book]:
        return await self._uow.books.list_for_owner(owner_user_id=UserId(user_id))

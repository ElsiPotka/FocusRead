from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.value_objects import UserId

if TYPE_CHECKING:
    from uuid import UUID


class ListBooks:
    def __init__(self, uow) -> None:
        self._uow = uow

    async def execute(self, *, owner_user_id: UUID):
        return await self._uow.books.list_for_owner(owner_user_id=UserId(owner_user_id))

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.value_objects import UserId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.label.entities import Label


class ListLabels:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, user_id: UUID) -> list[Label]:
        return await self._uow.labels.list_for_user(user_id=UserId(user_id))

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.label.value_objects import LabelId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class DeleteLabel:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, label_id: UUID, user_id: UUID) -> None:
        label = await self._uow.labels.get_for_owner(
            label_id=LabelId(label_id),
            user_id=UserId(user_id),
        )
        if label is None:
            raise NotFoundError("Label not found")

        await self._uow.labels.delete(label.id)
        await self._uow.commit()

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.label.value_objects import LabelId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class DeleteSystemLabel:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, label_id: UUID) -> None:
        label = await self._uow.labels.get_system(label_id=LabelId(label_id))
        if label is None:
            raise NotFoundError("System label not found")

        await self._uow.labels.delete(label.id)
        await self._uow.commit()

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.label.value_objects import LabelColor, LabelId, LabelName, LabelSlug
from app.infrastructure.persistence.models.mixins.slug import SlugMixin

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.label.entities import Label


class UpdateSystemLabel:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        label_id: UUID,
        name: str | None = None,
        color: str | None = None,
        clear_color: bool = False,
    ) -> Label:
        label = await self._uow.labels.get_system(label_id=LabelId(label_id))
        if label is None:
            raise NotFoundError("System label not found")

        if name is not None:
            slug = LabelSlug(SlugMixin.generate_slug(name))
            label.rename(name=LabelName(name), slug=slug)

        if color is not None:
            label.recolor(LabelColor(color))
        elif clear_color:
            label.recolor(None)

        await self._uow.labels.save(label)
        await self._uow.commit()
        return label

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.label.entities import Label
from app.domain.label.value_objects import LabelColor, LabelName, LabelSlug
from app.infrastructure.persistence.models.mixins.slug import SlugMixin

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork


class CreateSystemLabel:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        name: str,
        color: str | None = None,
    ) -> Label:
        slug = LabelSlug(SlugMixin.generate_slug(name))

        label = Label.create(
            name=LabelName(name),
            slug=slug,
            owner_user_id=None,
            color=LabelColor(color) if color else None,
            is_system=True,
        )
        await self._uow.labels.save(label)
        await self._uow.commit()
        return label

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.value_objects import UserId
from app.domain.label.entities import Label
from app.domain.label.value_objects import LabelColor, LabelName, LabelSlug
from app.infrastructure.persistence.models.mixins.slug import SlugMixin

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class CreateLabel:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        user_id: UUID,
        name: str,
        color: str | None = None,
    ) -> Label:
        slug = LabelSlug(SlugMixin.generate_slug(name))

        existing = await self._uow.labels.get_by_slug(
            slug=slug,
            user_id=UserId(user_id),
        )
        if existing is not None:
            return existing

        label = Label.create(
            name=LabelName(name),
            slug=slug,
            owner_user_id=UserId(user_id),
            color=LabelColor(color) if color else None,
        )
        await self._uow.labels.save(label)
        await self._uow.commit()
        return label

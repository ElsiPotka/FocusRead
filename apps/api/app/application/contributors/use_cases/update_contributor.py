from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.contributor.value_objects import (
    ContributorDisplayName,
    ContributorId,
    ContributorSortName,
)

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.contributor.entities import Contributor


class UpdateContributor:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        contributor_id: UUID,
        display_name: str,
        sort_name: str | None = None,
    ) -> Contributor:
        contributor = await self._uow.contributors.get(ContributorId(contributor_id))
        if contributor is None:
            raise NotFoundError("Contributor not found")

        contributor.rename(
            display_name=ContributorDisplayName(display_name),
            sort_name=ContributorSortName(sort_name) if sort_name else None,
        )
        await self._uow.contributors.save(contributor)
        await self._uow.commit()
        return contributor

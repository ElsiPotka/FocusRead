from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.theme.entities import Theme


class BrowseMarketplace:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "popular",
        query: str | None = None,
    ) -> tuple[list[Theme], int]:
        return await self._uow.themes.list_public(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            query=query,
        )

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.user.profile import UserProfile
    from app.types import PaginatedResult


class ListUsersForAdmin:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        page: int,
        per_page: int,
        cursor: str | None = None,
    ) -> PaginatedResult[UserProfile]:
        return await self._uow.users.paginate_profiles(
            page=page,
            per_page=per_page,
            cursor=cursor,
        )

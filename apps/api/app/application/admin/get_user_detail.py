from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.user.profile import UserProfile


class GetUserDetail:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, user_id: UUID) -> UserProfile:
        profile = await self._uow.users.get_profile(UserId(user_id))
        if profile is None:
            raise NotFoundError("User not found")
        return profile

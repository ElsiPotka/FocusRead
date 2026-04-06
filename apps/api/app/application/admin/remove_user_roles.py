from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.admin._helpers import get_user_or_raise, resolve_roles_or_raise
from app.domain.auth.value_objects import UserId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.role.entities import Role
    from app.domain.role.value_objects import RoleName


class RemoveUserRoles:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, user_id: UUID, role_names: list[RoleName]) -> list[Role]:
        user_id_vo = UserId(user_id)
        await get_user_or_raise(self._uow, user_id_vo)
        roles = await resolve_roles_or_raise(self._uow, role_names)
        await self._uow.roles.remove_many_from_user(
            user_id_vo,
            [role.id for role in roles],
        )
        await self._uow.commit()
        return await self._uow.roles.list_for_user(user_id_vo)

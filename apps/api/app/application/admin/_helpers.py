from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.auth.value_objects import UserId
    from app.domain.role.entities import Role
    from app.domain.role.value_objects import RoleName
    from app.domain.user.entities import User


async def get_user_or_raise(uow: AbstractUnitOfWork, user_id: UserId) -> User:
    user = await uow.users.get(user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user


async def resolve_roles_or_raise(
    uow: AbstractUnitOfWork,
    role_names: list[RoleName],
) -> list[Role]:
    requested_names = list(dict.fromkeys(role_names))
    roles = await uow.roles.get_by_names(requested_names)
    existing_names = {role.name for role in roles}
    missing = [
        role_name.value
        for role_name in requested_names
        if role_name not in existing_names
    ]
    if missing:
        raise NotFoundError(
            "One or more roles were not found",
            detail={"roles": missing},
        )
    return roles

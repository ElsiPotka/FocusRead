from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.application.admin.assign_user_roles import AssignUserRoles
from app.application.admin.list_users import ListUsersForAdmin
from app.application.admin.remove_user_roles import RemoveUserRoles
from app.domain.role.value_objects import RoleName
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import role_guard
from app.presentation.api.schemas.admin import (
    BulkUserRolesRequest,
    PaginatedAdminUsersResponse,
)
from app.presentation.api.schemas.pagination import PaginationParams  # noqa: TC001
from app.presentation.api.schemas.response import APIResponse
from app.presentation.api.schemas.users import UserRolesResponse

if TYPE_CHECKING:
    from app.domain.auth.entities import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
async def list_users(
    params: PaginationParams = Depends(),
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> APIResponse[PaginatedAdminUsersResponse]:
    page = await ListUsersForAdmin(uow).execute(
        page=params.page,
        per_page=params.per_page,
        cursor=params.cursor,
    )
    return APIResponse(
        success=True,
        data=PaginatedAdminUsersResponse.from_page(page),
        message="Users retrieved",
    )


@router.put("/users/{user_id}/roles")
async def assign_user_roles(
    user_id: uuid.UUID,
    body: BulkUserRolesRequest,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> APIResponse[UserRolesResponse]:
    roles = await AssignUserRoles(uow).execute(user_id=user_id, role_names=body.roles)
    return APIResponse(
        success=True,
        data=UserRolesResponse.from_roles(user_id, roles),
        message="Roles assigned",
    )


@router.delete("/users/{user_id}/roles")
async def remove_user_roles(
    user_id: uuid.UUID,
    body: BulkUserRolesRequest,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> APIResponse[UserRolesResponse]:
    roles = await RemoveUserRoles(uow).execute(user_id=user_id, role_names=body.roles)
    return APIResponse(
        success=True,
        data=UserRolesResponse.from_roles(user_id, roles),
        message="Roles removed",
    )

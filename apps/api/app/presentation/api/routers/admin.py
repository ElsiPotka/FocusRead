from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.application.admin.assign_user_roles import AssignUserRoles
from app.application.admin.create_system_label import CreateSystemLabel
from app.application.admin.delete_system_label import DeleteSystemLabel
from app.application.admin.list_system_labels import ListSystemLabels
from app.application.admin.list_users import ListUsersForAdmin
from app.application.admin.remove_user_roles import RemoveUserRoles
from app.application.admin.update_system_label import UpdateSystemLabel
from app.domain.role.value_objects import RoleName
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import role_guard
from app.presentation.api.schemas.admin import (
    BulkUserRolesRequest,
    PaginatedAdminUsersResponse,
)
from app.presentation.api.schemas.labels import (
    CreateLabelRequest,
    LabelResponse,
    UpdateLabelRequest,
)
from app.presentation.api.schemas.pagination import PaginationParams  # noqa: TC001
from app.presentation.api.schemas.response import (
    APIResponse,
    ListResponse,
    MessageResponse,
)
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


# --- System Labels ---


@router.post("/labels")
async def create_system_label(
    body: CreateLabelRequest,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> APIResponse[LabelResponse]:
    use_case = CreateSystemLabel(uow)
    label = await use_case.execute(name=body.name, color=body.color)
    return APIResponse(
        success=True,
        data=LabelResponse.from_entity(label),
        message="System label created",
    )


@router.get("/labels")
async def list_system_labels(
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> ListResponse[LabelResponse]:
    use_case = ListSystemLabels(uow)
    labels = await use_case.execute()
    data = [LabelResponse.from_entity(label) for label in labels]
    return ListResponse(
        success=True,
        data=data,
        count=len(data),
        message="System labels retrieved",
    )


@router.patch("/labels/{label_id}")
async def update_system_label(
    label_id: uuid.UUID,
    body: UpdateLabelRequest,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> APIResponse[LabelResponse]:
    use_case = UpdateSystemLabel(uow)
    label = await use_case.execute(
        label_id=label_id,
        name=body.name,
        color=body.color,
        clear_color=body.clear_color,
    )
    return APIResponse(
        success=True,
        data=LabelResponse.from_entity(label),
        message="System label updated",
    )


@router.delete("/labels/{label_id}")
async def delete_system_label(
    label_id: uuid.UUID,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = DeleteSystemLabel(uow)
    await use_case.execute(label_id=label_id)
    return MessageResponse(success=True, message="System label deleted")

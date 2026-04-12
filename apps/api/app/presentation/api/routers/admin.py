from __future__ import annotations

import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002

from app.application.admin.assign_user_roles import AssignUserRoles
from app.application.admin.create_system_label import CreateSystemLabel
from app.application.admin.delete_system_label import DeleteSystemLabel
from app.application.admin.get_platform_stats import GetPlatformStats, PlatformStats
from app.application.admin.get_user_books import GetUserBooks
from app.application.admin.get_user_detail import GetUserDetail
from app.application.admin.impersonate_user import ImpersonateUser
from app.application.admin.list_system_labels import ListSystemLabels
from app.application.admin.list_users import ListUsersForAdmin
from app.application.admin.remove_user_roles import RemoveUserRoles
from app.application.admin.update_system_label import UpdateSystemLabel
from app.domain.role.value_objects import RoleName
from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.auth.session_service import SessionService
from app.infrastructure.cache.redis import get_cache
from app.infrastructure.persistence.db import get_db
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import role_guard
from app.presentation.api.schemas.admin import (
    BulkUserRolesRequest,
    PaginatedAdminUsersResponse,
)
from app.presentation.api.schemas.auth import AuthResponse, TokenResponse, UserResponse
from app.presentation.api.schemas.books import BookResponse
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
from app.presentation.api.schemas.users import (
    CurrentUserProfileResponse,
    UserRolesResponse,
)

if TYPE_CHECKING:
    from app.domain.auth.entities import User
    from app.infrastructure.cache.redis_cache import RedisCache


class ImpersonateRequest(BaseModel):
    user_id: uuid.UUID | None = None
    email: EmailStr | None = None


class PlatformStatsResponse(BaseModel):
    total_users: int
    total_books: int
    books_pending: int
    books_processing: int
    books_ready: int
    books_error: int

    @staticmethod
    def from_stats(stats: PlatformStats) -> PlatformStatsResponse:
        return PlatformStatsResponse(
            total_users=stats.total_users,
            total_books=stats.total_books,
            books_pending=stats.books_pending,
            books_processing=stats.books_processing,
            books_ready=stats.books_ready,
            books_error=stats.books_error,
        )


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


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: uuid.UUID,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> APIResponse[CurrentUserProfileResponse]:
    use_case = GetUserDetail(uow)
    profile = await use_case.execute(user_id=user_id)
    return APIResponse(
        success=True,
        data=CurrentUserProfileResponse.from_profile(profile),
        message="User detail retrieved",
    )


@router.get("/users/{user_id}/books")
async def get_user_books(
    user_id: uuid.UUID,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> ListResponse[BookResponse]:
    use_case = GetUserBooks(uow)
    books = await use_case.execute(user_id=user_id)
    data = [BookResponse.from_entity(book) for book in books]
    return ListResponse(
        success=True,
        data=data,
        count=len(data),
        message="User books retrieved",
    )


@router.post("/impersonate")
async def impersonate_user(
    body: ImpersonateRequest,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> APIResponse[AuthResponse]:
    jwt_service = JWTService(cache)
    session_service = SessionService(cache)
    use_case = ImpersonateUser(uow, jwt_service, session_service)
    user, access_token, refresh_token = await use_case.execute(
        user_id=body.user_id,
        email=str(body.email) if body.email else None,
    )
    user_resp = UserResponse.from_entity(user)
    tokens = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=900,
    )
    return APIResponse(
        success=True,
        data=AuthResponse(user=user_resp, tokens=tokens),
        message="Impersonation tokens generated",
    )


# --- Platform Stats ---


@router.get("/stats")
async def get_platform_stats(
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    session: AsyncSession = Depends(get_db),
) -> APIResponse[PlatformStatsResponse]:
    use_case = GetPlatformStats(session)
    stats = await use_case.execute()
    return APIResponse(
        success=True,
        data=PlatformStatsResponse.from_stats(stats),
        message="Platform stats retrieved",
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

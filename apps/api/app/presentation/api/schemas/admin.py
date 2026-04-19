from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from app.domain.role.value_objects import RoleName  # noqa: TC001
from app.presentation.api.schemas.pagination import PaginatedResponse, PaginationMeta
from app.presentation.api.schemas.users import AdminUserProfileResponse

if TYPE_CHECKING:
    from app.domain.user.profile import UserProfile
    from app.types import PaginatedResult


class BulkUserRolesRequest(BaseModel):
    roles: list[RoleName] = Field(min_length=1)


class PaginatedAdminUsersResponse(PaginatedResponse[AdminUserProfileResponse]):
    @staticmethod
    def from_page(page: PaginatedResult[UserProfile]) -> PaginatedAdminUsersResponse:
        return PaginatedAdminUsersResponse(
            items=[
                AdminUserProfileResponse.from_profile(profile)
                for profile in page["items"]
            ],
            meta=PaginationMeta.model_validate(page["meta"]),
        )

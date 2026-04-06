from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Security

from app.application.auth.get_current_user_profile import GetCurrentUserProfile
from app.application.common.errors import ApplicationError
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.response import APIResponse
from app.presentation.api.schemas.users import CurrentUserProfileResponse

if TYPE_CHECKING:
    from app.domain.auth.entities import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[CurrentUserProfileResponse]:
    use_case = GetCurrentUserProfile(uow)
    profile = await use_case.execute(current_user.id.value)

    if profile is None:
        raise ApplicationError("User not found", status_code=404)

    return APIResponse(
        success=True,
        data=CurrentUserProfileResponse.from_profile(profile),
        message="Current user profile",
    )

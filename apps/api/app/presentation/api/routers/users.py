from __future__ import annotations

from fastapi import APIRouter, Depends

from app.application.auth.get_current_user_profile import GetCurrentUserProfile
from app.application.common.errors import ApplicationError
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.response import APIResponse
from app.presentation.api.schemas.users import CurrentUserProfileResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user),
    uow=Depends(get_uow),
) -> APIResponse[CurrentUserProfileResponse]:
    use_case = GetCurrentUserProfile(uow)
    profile = await use_case.execute(current_user.id.value)

    if profile is None:
        raise ApplicationError("User not found", status_code=404)

    user, accounts = profile
    return APIResponse(
        data=CurrentUserProfileResponse.from_entities(user, accounts),
        message="Current user profile",
    )

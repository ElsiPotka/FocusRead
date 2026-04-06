from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

import jwt
from fastapi import Cookie, Depends, Request, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from app.application.auth.get_current_user import GetCurrentUser
from app.application.common.errors import ApplicationError
from app.domain.auth.entities import User
from app.domain.role.value_objects import RoleName
from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.auth.session_service import SessionService
from app.infrastructure.cache.redis import get_cache
from app.infrastructure.config.settings import settings
from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork, get_uow

if TYPE_CHECKING:
    from app.infrastructure.cache.redis_cache import RedisCache


_OAUTH2_SCOPES = {
    "me": "Read the current authenticated user's profile.",
    RoleName.ADMIN.value: "Administrative access.",
    RoleName.MERCHANT.value: "Merchant-level access.",
    RoleName.CLIENT.value: "Client-level access.",
}

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/token",
    scopes=_OAUTH2_SCOPES,
    auto_error=False,
)


async def get_current_user(
    security_scopes: SecurityScopes,
    request: Request,
    token: Annotated[str | None, Security(oauth2_scheme)] = None,
    access_token_cookie: Annotated[str | None, Cookie(alias="access_token")] = None,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> User:
    raw_token = token or access_token_cookie
    if raw_token is None:
        raise ApplicationError("Not authenticated", status_code=401)

    jwt_service = JWTService(cache)
    session_service = SessionService(cache)

    _private_key, public_key = await jwt_service.get_or_create_key_pair(uow)

    try:
        payload = jwt_service.decode_access_token(raw_token, public_key)
    except jwt.ExpiredSignatureError as exc:
        raise ApplicationError("Access token expired", status_code=401) from exc
    except jwt.InvalidTokenError as exc:
        raise ApplicationError("Invalid access token", status_code=401) from exc

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise ApplicationError("Invalid access token", status_code=401)

    try:
        user_id = UUID(user_id_str)
    except ValueError as exc:
        raise ApplicationError("Invalid access token", status_code=401) from exc

    token_scopes = str(payload.get("scope", "")).split()
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise ApplicationError("Not enough permissions", status_code=403)

    use_case = GetCurrentUser(uow, session_service)
    user = await use_case.execute(user_id)

    if user is None:
        raise ApplicationError("User not found", status_code=401)

    if not user.is_active:
        raise ApplicationError("User account is inactive", status_code=403)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def role_guard(required_role: RoleName):
    async def guard(
        current_user: User = Security(get_current_user, scopes=[required_role.value]),
    ) -> User:
        return current_user

    guard.__name__ = f"require_{required_role.value.lower()}_role"
    return guard

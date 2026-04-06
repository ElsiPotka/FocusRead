from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

import jwt
from fastapi import Cookie, Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.application.auth.get_current_user import GetCurrentUser
from app.application.common.errors import ApplicationError
from app.domain.auth.entities import User
from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.auth.session_service import SessionService
from app.infrastructure.cache.redis import get_cache
from app.infrastructure.config.settings import settings
from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork, get_uow

if TYPE_CHECKING:
    from app.infrastructure.cache.redis_cache import RedisCache

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/token",
    auto_error=False,
)


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
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

    use_case = GetCurrentUser(uow, session_service)
    user = await use_case.execute(user_id)

    if user is None:
        raise ApplicationError("User not found", status_code=401)

    if not user.is_active:
        raise ApplicationError("User account is inactive", status_code=403)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

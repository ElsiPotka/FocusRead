from __future__ import annotations

from typing import TYPE_CHECKING, Never

from fastapi import APIRouter, Cookie, Depends, Query, Request, Response, status
from fastapi.responses import RedirectResponse  # noqa: TC002
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TC002

from app.application.auth.login import LoginUser
from app.application.auth.logout import LogoutUser
from app.application.auth.oauth_callback import HandleOAuthCallback
from app.application.auth.refresh_token import RefreshAccessToken
from app.application.auth.register import RegisterUser
from app.domain.auth.errors import (
    AuthError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    SessionExpiredError,
)
from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.auth.oauth import oauth
from app.infrastructure.auth.session_service import SessionService
from app.infrastructure.cache.redis import get_cache
from app.infrastructure.config.settings import settings
from app.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork, get_uow
from app.presentation.api.middleware.rate_limiter import limiter
from app.presentation.api.schemas.auth import (
    AuthResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.presentation.api.schemas.response import APIResponse, MessageResponse

if TYPE_CHECKING:
    from app.domain.auth.entities import User
    from app.infrastructure.cache.redis_cache import RedisCache

router = APIRouter(prefix="/auth", tags=["auth"])

_AUTH_ERROR_MAP: dict[type[AuthError], tuple[int, str]] = {
    InvalidCredentialsError: (401, "Invalid email or password"),
    EmailAlreadyExistsError: (409, "A user with this email already exists"),
    SessionExpiredError: (401, "Session has expired"),
    InvalidRefreshTokenError: (401, "Invalid or expired refresh token"),
    InactiveUserError: (403, "User account is inactive"),
}


def _build_token_response(access_token: str, refresh_token: str) -> TokenResponse:
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _set_auth_cookies(
    response: Response, access_token: str, refresh_token: str
) -> None:
    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax",
        secure=settings.AUTH_COOKIE_SECURE_RESOLVED,
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        samesite="lax",
        secure=settings.AUTH_COOKIE_SECURE_RESOLVED,
        path="/",
    )


def _deliver_tokens(
    response: Response,
    user: User,
    access_token: str,
    refresh_token: str,
    *,
    is_mobile: bool,
) -> APIResponse[AuthResponse] | APIResponse[UserResponse]:
    user_resp = UserResponse.from_entity(user)

    if is_mobile:
        tokens = _build_token_response(access_token, refresh_token)
        return APIResponse(
            success=True,
            data=AuthResponse(user=user_resp, tokens=tokens),
            message="Authenticated",
        )

    _set_auth_cookies(response, access_token, refresh_token)
    return APIResponse(success=True, data=user_resp, message="Authenticated")


def _handle_auth_error(exc: AuthError) -> Never:
    from app.application.common.errors import ApplicationError

    status_code, message = _AUTH_ERROR_MAP.get(type(exc), (400, str(exc)))
    raise ApplicationError(message, status_code=status_code)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    response: Response,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
    client: str | None = Query(None),
) -> APIResponse[AuthResponse] | APIResponse[UserResponse]:
    jwt_service = JWTService(cache)
    session_service = SessionService(cache)
    use_case = RegisterUser(uow, jwt_service, session_service)

    try:
        result = await use_case.execute(
            name=body.name,
            surname=body.surname,
            email=body.email,
            password=body.password,
        )
    except AuthError as exc:
        _handle_auth_error(exc)

    user, access_token, refresh_token = result
    return _deliver_tokens(
        response, user, access_token, refresh_token, is_mobile=client == "mobile"
    )


@router.post("/token")
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
    client: str | None = Query(None),
) -> APIResponse[AuthResponse] | APIResponse[UserResponse]:
    jwt_service = JWTService(cache)
    session_service = SessionService(cache)
    use_case = LoginUser(uow, jwt_service, session_service)

    try:
        result = await use_case.execute(
            email=form_data.username,
            password=form_data.password,
        )
    except AuthError as exc:
        _handle_auth_error(exc)

    user, access_token, refresh_token = result
    return _deliver_tokens(
        response, user, access_token, refresh_token, is_mobile=client == "mobile"
    )


@router.post("/token/refresh")
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    refresh_token_cookie: str | None = Cookie(None, alias="refresh_token"),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
    client: str | None = Query(None),
) -> APIResponse[AuthResponse] | APIResponse[UserResponse]:
    raw_refresh = (body.refresh_token if body else None) or refresh_token_cookie
    if not raw_refresh:
        from app.application.common.errors import ApplicationError

        raise ApplicationError("Refresh token is required", status_code=401)

    jwt_service = JWTService(cache)
    session_service = SessionService(cache)
    use_case = RefreshAccessToken(uow, jwt_service, session_service)

    try:
        result = await use_case.execute(
            raw_refresh_token=raw_refresh,
        )
    except AuthError as exc:
        _handle_auth_error(exc)

    user, access_token, new_refresh = result
    return _deliver_tokens(
        response, user, access_token, new_refresh, is_mobile=client == "mobile"
    )


@router.post("/logout")
@limiter.limit("20/minute")
async def logout(
    request: Request,
    response: Response,
    body: RefreshRequest | None = None,
    refresh_token_cookie: str | None = Cookie(None, alias="refresh_token"),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> MessageResponse:
    raw_refresh = (body.refresh_token if body else None) or refresh_token_cookie
    if not raw_refresh:
        from app.application.common.errors import ApplicationError

        raise ApplicationError("Refresh token is required", status_code=401)

    session_service = SessionService(cache)
    use_case = LogoutUser(uow, session_service)

    try:
        await use_case.execute(raw_refresh_token=raw_refresh)
    except AuthError as exc:
        _handle_auth_error(exc)

    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return MessageResponse(success=True, message="Logged out")


@router.get("/google/authorize")
@limiter.limit("10/minute")
async def google_authorize(request: Request) -> RedirectResponse:
    redirect_uri = (
        f"{settings.FRONTEND_URL}{settings.API_V1_PREFIX}/auth/google/callback"
    )
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
@limiter.limit("10/minute")
async def google_callback(
    request: Request,
    response: Response,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
    client: str | None = Query(None),
) -> APIResponse[AuthResponse] | APIResponse[UserResponse]:
    token_data = await oauth.google.authorize_access_token(request)
    user_info = token_data.get("userinfo", {})

    jwt_service = JWTService(cache)
    session_service = SessionService(cache)
    use_case = HandleOAuthCallback(uow, jwt_service, session_service)

    user, access_token, refresh_token = await use_case.execute(
        provider="google",
        oauth_user_info=user_info,
        oauth_tokens=token_data,
    )

    return _deliver_tokens(
        response, user, access_token, refresh_token, is_mobile=client == "mobile"
    )


@router.get("/apple/authorize")
@limiter.limit("10/minute")
async def apple_authorize(request: Request) -> RedirectResponse:
    redirect_uri = (
        f"{settings.FRONTEND_URL}{settings.API_V1_PREFIX}/auth/apple/callback"
    )
    return await oauth.apple.authorize_redirect(request, redirect_uri)


@router.get("/apple/callback")
@limiter.limit("10/minute")
async def apple_callback(
    request: Request,
    response: Response,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
    client: str | None = Query(None),
) -> APIResponse[AuthResponse] | APIResponse[UserResponse]:
    token_data = await oauth.apple.authorize_access_token(request)
    user_info = token_data.get("userinfo", {})

    jwt_service = JWTService(cache)
    session_service = SessionService(cache)
    use_case = HandleOAuthCallback(uow, jwt_service, session_service)

    user, access_token, refresh_token = await use_case.execute(
        provider="apple",
        oauth_user_info=user_info,
        oauth_tokens=token_data,
    )

    return _deliver_tokens(
        response, user, access_token, refresh_token, is_mobile=client == "mobile"
    )

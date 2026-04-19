from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, cast

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.application.common.errors import ApplicationError
from app.domain.auth.errors import (
    AuthError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    SessionExpiredError,
)
from app.infrastructure.config.settings import settings
from app.infrastructure.logging.logger import log

_AUTH_ERROR_MAP: dict[type[AuthError], tuple[int, str]] = {
    InvalidCredentialsError: (401, "Invalid email or password"),
    EmailAlreadyExistsError: (409, "A user with this email already exists"),
    SessionExpiredError: (401, "Session has expired"),
    InvalidRefreshTokenError: (401, "Invalid or expired refresh token"),
    InactiveUserError: (403, "User account is inactive"),
}

if TYPE_CHECKING:
    from fastapi import FastAPI, Request
    from starlette.types import ExceptionHandler

    from app.types import JSONObject, JSONValue


def _make_json_safe(value: object) -> JSONValue:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Exception):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [_make_json_safe(item) for item in value]
    return str(value)


async def _application_error_handler(
    _request: Request,
    exc: ApplicationError,
) -> JSONResponse:
    body: JSONObject = {"success": False, "message": exc.message}

    if exc.detail is not None:
        body["detail"] = _make_json_safe(exc.detail)

    log.warning("Application error: {}", exc.message)
    return JSONResponse(status_code=exc.status_code, content=body)


async def _validation_error_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = _make_json_safe(exc.errors())
    log.warning("Validation error: {}", errors)

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "detail": errors,
        },
    )


async def _unhandled_error_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    log.exception("Unhandled exception: {}", exc)

    body: JSONObject = {
        "success": False,
        "message": "Internal server error",
    }

    if not settings.IS_PRODUCTION:
        body["detail"] = traceback.format_exc()

    return JSONResponse(status_code=500, content=body)


async def _auth_error_handler(
    _request: Request,
    exc: AuthError,
) -> JSONResponse:
    status_code, message = _AUTH_ERROR_MAP.get(type(exc), (400, str(exc)))
    log.warning("Auth error: {}", message)
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        AuthError,
        cast("ExceptionHandler", _auth_error_handler),
    )
    app.add_exception_handler(
        ApplicationError,
        cast("ExceptionHandler", _application_error_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast("ExceptionHandler", _validation_error_handler),
    )
    app.add_exception_handler(Exception, _unhandled_error_handler)

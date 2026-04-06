from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Any, cast

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.application.common.errors import ApplicationError
from app.infrastructure.config.settings import settings
from app.infrastructure.logging.logger import log

if TYPE_CHECKING:
    from fastapi import FastAPI, Request
    from starlette.types import ExceptionHandler


def _make_json_safe(value: Any) -> Any:
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
    body: dict[str, Any] = {"success": False, "message": exc.message}

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

    body: dict[str, Any] = {
        "success": False,
        "message": "Internal server error",
    }

    if not settings.IS_PRODUCTION:
        body["detail"] = traceback.format_exc()

    return JSONResponse(status_code=500, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        ApplicationError,
        cast("ExceptionHandler", _application_error_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast("ExceptionHandler", _validation_error_handler),
    )
    app.add_exception_handler(Exception, _unhandled_error_handler)

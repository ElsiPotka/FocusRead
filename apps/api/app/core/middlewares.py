from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config.settings import settings
from app.middleware.request_id import RequestIdMiddleware

if TYPE_CHECKING:
    from fastapi import FastAPI


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(cast("type", SlowAPIMiddleware))
    app.add_middleware(
        cast("type", CORSMiddleware),
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        cast("type", TrustedHostMiddleware),
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    app.add_middleware(
        cast("type", RequestIdMiddleware),
        max_length=settings.REQUEST_ID_MAX_LENGTH,
        trust_proxy=settings.IS_BEHIND_PROXY,
    )

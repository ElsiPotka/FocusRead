from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.infrastructure.config.settings import settings
from app.presentation.api.middleware.request_id import RequestIdMiddleware

if TYPE_CHECKING:
    from fastapi import FastAPI


def register_middleware(app: FastAPI) -> None:
    # Middleware executes in REVERSE registration order.
    # Register innermost (closest to app) first, outermost last.

    # 5. GZip — compress responses ≥1 KB (chunk payloads are 15-25 KB)
    app.add_middleware(cast("type", GZipMiddleware), minimum_size=1000, compresslevel=5)

    # 4. Rate limiting
    app.add_middleware(cast("type", SlowAPIMiddleware))

    # 3. CORS
    app.add_middleware(
        cast("type", CORSMiddleware),
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Trusted hosts
    app.add_middleware(
        cast("type", TrustedHostMiddleware),
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

    # 1. Request ID (registered last, executes first)
    app.add_middleware(
        cast("type", RequestIdMiddleware),
        max_length=settings.REQUEST_ID_MAX_LENGTH,
        trust_proxy=settings.IS_BEHIND_PROXY,
    )

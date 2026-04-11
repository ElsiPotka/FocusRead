from contextlib import asynccontextmanager
from typing import Any, cast

import uvloop
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import app.infrastructure.persistence.models as _models  # noqa: F401
from app.infrastructure.bootstrap import shutdown_app_events, startup_app_events
from app.infrastructure.config.settings import settings
from app.presentation.api.exception_handlers import register_exception_handlers
from app.presentation.api.middleware.rate_limiter import limiter
from app.presentation.api.middlewares import register_middleware
from app.presentation.api.routers import register_routers

uvloop.install()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await startup_app_events()
    try:
        yield
    finally:
        await shutdown_app_events()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url=None if settings.IS_PRODUCTION else "/docs",
        redoc_url=None if settings.IS_PRODUCTION else "/redoc",
        openapi_url=None if settings.IS_PRODUCTION else "/openapi.json",
        swagger_ui_parameters={
            "persistAuthorization": True,
            "displayRequestDuration": True,
        },
        swagger_ui_init_oauth={
            "usePkceWithAuthorizationCodeGrant": True,
        },
    )

    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        cast("Any", _rate_limit_exceeded_handler),
    )
    register_exception_handlers(app)
    register_middleware(app)
    register_routers(app)

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, Any]:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    return app


app = create_application()

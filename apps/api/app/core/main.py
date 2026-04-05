from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config.exception_handlers import register_exception_handlers
from app.config.settings import settings
from app.core import domain_models as _domain_models  # noqa: F401
from app.core.bootstrap import shutdown_app_events, startup_app_events
from app.core.middlewares import register_middleware
from app.core.routers import register_routers
from app.middleware.rate_limiter import limiter


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

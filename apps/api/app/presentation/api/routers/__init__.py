from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.config.settings import settings
from app.presentation.api.routers.auth import router as auth_router
from app.presentation.api.routers.health import router as health_router
from app.presentation.api.routers.users import router as users_router

if TYPE_CHECKING:
    from fastapi import FastAPI


def register_routers(app: FastAPI) -> None:
    app.include_router(health_router, prefix=settings.API_V1_PREFIX)
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(users_router, prefix=settings.API_V1_PREFIX)

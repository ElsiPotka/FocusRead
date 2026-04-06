from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.config.settings import settings
from app.presentation.api.routers.health import router as health_router

if TYPE_CHECKING:
    from fastapi import FastAPI


def register_routers(app: FastAPI) -> None:
    app.include_router(health_router, prefix=settings.API_V1_PREFIX)

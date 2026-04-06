from fastapi import APIRouter

from app.infrastructure.cache.redis import check_redis_health
from app.infrastructure.config.settings import settings
from app.presentation.api.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    redis_is_healthy = await check_redis_health()
    return HealthResponse(
        status="ok" if redis_is_healthy else "degraded",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        redis="ok" if redis_is_healthy else "unavailable",
        celery="configured",
    )

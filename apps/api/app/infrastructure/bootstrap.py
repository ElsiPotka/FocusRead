from app.infrastructure.cache.redis import close_redis, init_redis
from app.infrastructure.config.settings import settings
from app.infrastructure.logging.logger import log, setup_logging
from app.infrastructure.persistence.db import close_db, init_db


def one_time_setup() -> None:
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


async def startup_app_events() -> None:
    one_time_setup()
    setup_logging()

    log.info("Starting {} ({})", settings.APP_NAME, settings.ENVIRONMENT)
    await init_db(check_connection=settings.DB_EAGER_CONNECT)
    await init_redis(check_connection=settings.REDIS_EAGER_CONNECT)


async def shutdown_app_events() -> None:
    await close_redis()
    await close_db()
    log.info("Shutdown complete.")

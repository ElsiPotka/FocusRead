from app.config.db import close_db, init_db
from app.config.logger import log, setup_logging
from app.config.settings import settings


def one_time_setup() -> None:
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


async def startup_app_events() -> None:
    one_time_setup()
    setup_logging()

    log.info("Starting {} ({})", settings.APP_NAME, settings.ENVIRONMENT)
    await init_db(check_connection=settings.DB_EAGER_CONNECT)


async def shutdown_app_events() -> None:
    await close_db()
    log.info("Shutdown complete.")

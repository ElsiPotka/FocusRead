import logging
import sys

from loguru import logger

from app.config.settings import settings


class LoggerConfig:
    def __init__(self) -> None:
        self.log_dir = settings.STORAGE_DIR / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        logger.remove()

        self._setup_console()
        self._setup_file_logging()

    def _setup_console(self) -> None:
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<dim>{extra[request_id]}</dim> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )

        if settings.ENVIRONMENT == "local":
            logger.add(
                sys.stdout,
                format=console_format,
                level="DEBUG",
                colorize=True,
                backtrace=True,
                diagnose=True,
            )
        else:
            logger.add(
                sys.stderr,
                format=console_format,
                level="INFO",
                colorize=True,
                backtrace=False,
                diagnose=False,
            )

    def _setup_file_logging(self) -> None:
        retention_days = 30 if settings.ENVIRONMENT == "production" else 7

        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{extra[request_id]} | {extra[client_ip]} | "
            "{name}:{function}:{line} - {message}"
        )

        logger.add(
            self.log_dir / "app.log",
            format=file_format,
            level="INFO",
            rotation="00:00",
            retention=f"{retention_days} days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=settings.ENVIRONMENT == "local",
        )

        logger.add(
            self.log_dir / "app-error.log",
            format=file_format,
            level="ERROR",
            rotation="00:00",
            retention=f"{retention_days} days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=settings.ENVIRONMENT == "local",
        )

        if settings.ENVIRONMENT == "local":
            logger.add(
                self.log_dir / "app-debug.log",
                format=file_format,
                level="DEBUG",
                rotation="00:00",
                retention=f"{retention_days} days",
                compression="zip",
                enqueue=True,
                backtrace=True,
                diagnose=True,
            )


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def setup_logging() -> None:
    LoggerConfig()
    logger.configure(extra={"request_id": "", "client_ip": ""})

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    if settings.ENVIRONMENT == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

    logger.info("Logger configured for {} environment", settings.ENVIRONMENT)


log = logger

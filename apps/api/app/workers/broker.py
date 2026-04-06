from celery import Celery

import app.infrastructure.persistence.models as _models  # noqa: F401
from app.infrastructure.config.settings import settings

celery_app = Celery(
    "focusread",
    include=["app.workers.task"],
)

celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    result_expires=settings.CACHE_DEFAULT_TTL_SECONDS,
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(["app.workers"], related_name="task")

from app.workers import scheduler as _scheduler  # noqa: F401, E402
from app.workers import task as _task  # noqa: F401, E402

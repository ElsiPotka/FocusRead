# Workers

This folder contains the Celery integration for background work.

## Files

- `broker.py`: Celery app configuration
- `scheduler.py`: scheduled task registration
- `task.py`: task implementations

## Notes

- the Celery app reads broker and backend settings from `app.infrastructure.config.settings`
- persistence models are imported during worker boot so SQLAlchemy metadata is available consistently
- keep long-running or asynchronous background workflows here instead of inside HTTP request handlers

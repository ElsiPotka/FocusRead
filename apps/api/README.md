# FocusRead API

FastAPI backend scaffold for the FocusRead monorepo.

## Run

```bash
uv sync --dev
uv run fastapi dev app/core/main.py
```

## Redis And Celery

```bash
uv run celery -A app.workers.broker.celery_app worker --loglevel=info
uv run celery -A app.workers.broker.celery_app beat --loglevel=info
```

## Migrations

```bash
uv run alembic upgrade head
uv run alembic revision -m "create_books_table"
uv run alembic revision --autogenerate -m "add_book_chunks"
```

Migration filenames are timestamp-prefixed in `YYYY-MM-DD_HHMM_<rev>_<slug>.py` format.

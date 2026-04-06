# Alembic

This folder contains the database migration environment for the API.

## What Lives Here

- `env.py`: loads settings, imports model metadata, and configures Alembic
- `script.py.mako`: revision template
- `versions/`: migration history

## Important Notes

- Alembic gets metadata from `app.infrastructure.persistence.models`
- if you add a new SQLAlchemy model, export it from `app/infrastructure/persistence/models/__init__.py`
- `env.py` currently excludes some tables through `_EXCLUDED_TABLES`; review that list before relying on `--autogenerate`
- migrations use `uuidv7()` server defaults, so the database must provide that function

## Typical Workflow

From `apps/api`:

```bash
uv run alembic upgrade head
uv run alembic revision -m "describe_change"
uv run alembic revision --autogenerate -m "describe_change"
```

Always review generated migrations manually before applying them.

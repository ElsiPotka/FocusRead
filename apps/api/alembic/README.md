# Alembic

This folder contains the database migration environment for the API.

## Current Progress

The migration history now covers the main backend schema delivered so far:

- users, accounts, sessions, JWT signing keys, roles, and user-role links
- books and book chunks
- reading sessions and reading stats
- user book state
- contributors
- shelves
- labels and seeded system labels
- book TOC entries
- bookmarks

In practice, the migration set now matches the implemented backend feature slices much
more than a scaffold or partial plan.

## What Lives Here

- `env.py`: loads settings, imports model metadata, and configures Alembic
- `script.py.mako`: revision template
- `versions/`: migration history

## Important Notes

- Alembic gets metadata from `app.infrastructure.persistence.models`
- if you add a new SQLAlchemy model, export it from
  `app/infrastructure/persistence/models/__init__.py`
- `env.py` currently excludes some tables through `_EXCLUDED_TABLES`; review that list
  before relying on `--autogenerate`
- migrations use `uuidv7()` server defaults, so the database must provide that
  function
- reusable PostgreSQL full-text search helpers live in
  `app/infrastructure/persistence/migrations/search.py`
- for `SearchMixin` models, use PostgreSQL stored generated `tsvector` columns plus a
  `GIN` index instead of triggers or ad hoc application-side updates

## Typical Workflow

From `apps/api`:

```bash
uv run alembic upgrade head
uv run alembic revision -m "describe_change"
uv run alembic revision --autogenerate -m "describe_change"
```

Always review generated migrations manually before applying them.

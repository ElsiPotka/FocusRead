# Alembic

This folder contains the database migration environment for the API.

## Current Progress

The migration history covers the schema reset toward the current backend model:

- users, accounts, sessions, JWT signing keys, roles, and user-role links
- canonical `books`, `book_assets`, `marketplace_listings`, and `library_items`
- asset-scoped book chunks and TOC entries
- library-item-scoped bookmarks, reading sessions, and reading stats
- contributors
- shelves via `shelf_items`
- labels via `library_labels` and `library_item_labels`
- themes and theme-like tables
- removal of `user_book_state` in revision `0031`

This matches the active refactor target in
[`../../docs/BACKEND_IMPLEMENTATION_PLAN.md`](../../docs/BACKEND_IMPLEMENTATION_PLAN.md),
not a finished application rollout. Application-layer cutover continues in later
plan phases.

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

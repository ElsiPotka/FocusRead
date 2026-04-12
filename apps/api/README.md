# FocusRead API

FastAPI backend for the FocusRead monorepo.

As of 2026-04-12 this service is no longer a scaffold. It is the most complete part
of the repo and already covers most backend work needed for the product described in
[`../../docs/IDEA.md`](../../docs/IDEA.md).

## Current Backend Progression

Implemented end-to-end slices:

- auth and RBAC: register, login, refresh, logout, current user, Google and Apple
  OAuth callbacks, role-based scopes, and admin role assignment/removal
- book ingestion: PDF upload, local file storage, Celery processing, Redis-backed
  progress events, chunk persistence, chunk caching, metadata CRUD, search, and
  filtered library views
- reading flow: chunk resolution, session resume, progress upsert, per-book stats,
  summary stats, and user book state preferences
- library organization: shelves, labels, bookmarks, contributors, favorites,
  archive, completed, and continue-reading helpers
- admin curation: user listing plus system-label CRUD
- supporting infrastructure: Alembic migrations, async SQLAlchemy repositories,
  Redis cache helpers, typed settings, middleware, and worker tasks

The backend rollout described in
[`../../docs/BACKEND_IMPLEMENTATION_PLAN.md`](../../docs/BACKEND_IMPLEMENTATION_PLAN.md)
is largely reflected in code. The biggest remaining product work now sits outside
this service: web/mobile clients, end-to-end deployment validation, and final
polish. One visible backend gap is that book TOC storage exists, but the PDF worker
still finishes with `toc_extracted = false`, so automatic TOC extraction is not yet
fully wired into processing.

## Stack Snapshot

As of 2026-04-12 this service targets:

- Python 3.14+
- FastAPI `0.135.3+`
- SQLAlchemy asyncio `2.0.44+`
- Alembic `1.16.5+`
- Celery `5.5.3+`
- Redis client `6.2.0+`
- PostgreSQL via `asyncpg 0.30.0+`
- `uv` for environment and command execution

The local deployment scaffold in `../deployment/docker-compose.yml` currently uses
PostgreSQL 17 and Redis 7. The persistence layer still relies on a database-side
`uuidv7()` SQL function.

## Architecture Overview

This service keeps a DDD-style split:

- `domain`: business entities, value objects, repository contracts, and domain errors
- `application`: use cases that orchestrate domain objects through a unit of work
- `infrastructure`: SQLAlchemy, Redis, auth services, storage, settings, logging, DI
- `presentation`: FastAPI routers, schemas, middleware, and exception mapping
- `workers`: Celery broker, PDF processing, tokenizer, and async background tasks

Project tree:

```text
apps/api/
├── alembic/                    # Migration environment and revision history
├── app/
│   ├── application/           # Use cases for auth, books, reading, library, admin
│   ├── domain/                # Pure business logic and repository interfaces
│   ├── infrastructure/        # DB, Redis, auth, config, storage, logging, DI
│   ├── presentation/          # FastAPI HTTP layer
│   ├── workers/               # Celery broker, tokenizer, PDF processing, tasks
│   └── main.py                # FastAPI entrypoint
├── tests/                     # Domain, use-case, API, infra, and worker tests
├── storage/                   # Local runtime files such as uploads and logs
├── .env.example               # Local configuration template
├── pyproject.toml             # Dependencies and tool configuration
└── README.md
```

Layer-specific documentation:

- `app/README.md`
- `alembic/README.md`
- `app/application/README.md`
- `app/application/common/README.md`
- `app/domain/README.md`
- `app/infrastructure/README.md`
- `app/infrastructure/persistence/README.md`
- `app/presentation/README.md`
- `app/presentation/api/README.md`
- `app/workers/README.md`
- `tests/README.md`

## Local Development

Run all commands from `apps/api`.

```bash
cp .env.example .env
docker compose -f ../deployment/docker-compose.yml up postgres redis -d
uv sync --dev
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

What this does:

- `.env` provides settings consumed by `app.infrastructure.config.settings`
- `docker compose ... up postgres redis -d` starts the two services the API needs for
  local work
- `uv sync --dev` installs runtime and development dependencies
- `alembic upgrade head` creates or upgrades the schema
- `fastapi dev app/main.py` starts the API with reload

After startup:

- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health endpoint: `http://127.0.0.1:8000/api/v1/health`

If you want upload processing to run end to end, start a worker in a separate shell:

```bash
uv run celery -A app.workers.broker.celery_app worker --loglevel=info
```

Optional beat process:

```bash
uv run celery -A app.workers.broker.celery_app beat --loglevel=info
```

## Testing And Quality Checks

From `apps/api`:

```bash
uv run ruff check . --fix
uv run ruff format .
uvx ty check
uvx basedpyright
uv run pytest
```

Useful focused commands:

```bash
uv run pytest tests/domain
uv run pytest tests/usecase
uv run pytest tests/presentation
uv run pytest tests/workers
```

## Migrations

Upgrade the database:

```bash
uv run alembic upgrade head
```

Create a manual revision:

```bash
uv run alembic revision -m "describe_change"
```

Create an autogenerated revision:

```bash
uv run alembic revision --autogenerate -m "describe_change"
```

Migration filenames are timestamp-prefixed in
`YYYY-MM-DD_HHMM_<rev>_<slug>.py` format. Always review autogenerated
revisions before applying them.

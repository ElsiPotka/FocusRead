# App Package

`app/` contains the runtime code for the API service.

## Current Progress

This package contains the runtime code for the API service and the ongoing schema
refactor described in
[`../../../docs/BACKEND_IMPLEMENTATION_PLAN.md`](../../../docs/BACKEND_IMPLEMENTATION_PLAN.md).
The current state is:

- auth, sessions, and role-based access control
- book upload, async PDF chunk processing, chunk retrieval, and book metadata
- canonical catalog and access aggregates: `Book`, `BookAsset`, `LibraryItem`, and
  `MarketplaceListing`
- reading sessions, reading stats, bookmarks, shelves, and labels re-anchored to
  the new aggregate model in the domain and persistence layers
- contributors, search helpers, and admin basics
- admin user listing, role management, and system-label curation

Some application, router, and worker callers still speak the older book-centric
signatures by design. Those migrations are tracked in plan phases `R3` through `R6`.

## Main Folders

- `application/`: use cases that coordinate domain logic and transactional work
- `domain/`: pure business logic, repository contracts, value objects, and errors
- `infrastructure/`: SQLAlchemy, Redis, auth, storage, config, logging, and DI
- `presentation/`: FastAPI routers, schemas, middleware, and exception handling
- `workers/`: Celery broker, tokenizer, PDF processing, and background tasks
- `main.py`: FastAPI application entrypoint

## Dependency Direction

The intended dependency flow is:

```text
presentation -> application -> domain
infrastructure -> domain
presentation -> infrastructure
application -> infrastructure only through shared application-facing contracts such as the unit of work
```

## Rule Of Thumb

When adding or extending a feature, keep the vertical slice order:

1. `domain`
2. `infrastructure/persistence`
3. `application`
4. `presentation`
5. `tests`

Most new work should extend an existing slice rather than introduce a parallel
architecture.

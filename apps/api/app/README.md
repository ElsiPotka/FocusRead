# App Package

`app/` contains the runtime code for the API service.

## Current Progress

This package now contains the full backend slice for the current FocusRead MVP, not
just scaffolding. End-to-end flows already exist for:

- auth, sessions, and role-based access control
- book upload, async PDF chunk processing, chunk retrieval, and book metadata
- reading sessions, reading stats, and user book state
- shelves, labels, bookmarks, contributors, and discovery/search helpers
- admin user listing, role management, and system-label curation

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

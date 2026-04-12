# Persistence

This package contains the async SQLAlchemy persistence implementation.

## Current Progress

The persistence layer now covers the main backend schema from the implementation
plan:

- identity: users, accounts, sessions, JWT signing keys, roles, and user-role links
- reading: books, book chunks, TOC entries, reading sessions, reading stats, and user
  book state
- organization: contributors, shelves, labels, bookmarks, and related join tables

Search support is already wired for searchable aggregates through stored generated
`tsvector` columns and `GIN` indexes.

## Files And Folders

- `db.py`: async engine and session lifecycle
- `models/`: SQLAlchemy models, mixins, and shared base classes
- `repositories/`: concrete repository implementations
- `migrations/search.py`: shared helpers for generated search columns and indexes
- `pagination.py`: shared pagination helpers
- `unit_of_work.py`: concrete SQLAlchemy unit of work

## Model Rules

- put persistence-only columns and relationships in SQLAlchemy models
- inherit from `BaseModel` when the table should have `id`, `created_at`, and
  `updated_at`
- export new models from `models/__init__.py` so Alembic sees them
- when adding relationships, use explicit loading strategies such as
  `selectinload(...)` or `lazy="selectin"` instead of relying on incidental lazy
  loads
- use `SearchMixin` with a stored generated `tsvector` column plus a `GIN` index in
  migrations
- use `MetadataMixin` only for flexible non-query-critical data
- use `VersionMixin` on aggregates where optimistic locking is useful
- use `SlugMixin` only where normalized identifiers are part of the aggregate design

## Repository Rules

- repositories translate between SQLAlchemy models and domain entities
- repositories should return domain objects, not ORM models
- complex query behavior belongs here, not in routers or use cases

## Unit Of Work

`SqlAlchemyUnitOfWork` is the composition root for repository access inside
transactional use cases. Any repository used from the application layer must be
exposed there.

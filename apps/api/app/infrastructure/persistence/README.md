# Persistence

This package contains the async SQLAlchemy persistence implementation.

## Files And Folders

- `db.py`: async engine and session lifecycle
- `models/`: SQLAlchemy models and shared base classes
- `repositories/`: concrete repository implementations
- `pagination.py`: shared pagination helpers
- `unit_of_work.py`: concrete SQLAlchemy unit of work

## Model Rules

- put persistence-only columns and relationships in SQLAlchemy models
- inherit from `BaseModel` when the table should have `id`, `created_at`, and `updated_at`
- export new models from `models/__init__.py` so Alembic sees them
- when adding relationships, use explicit loading strategies such as `selectinload(...)` or `lazy="selectin"` instead of relying on incidental lazy loads
- use `SearchMixin` on searchable aggregates and pair it with a stored generated `tsvector` column plus a `GIN` index in migrations
- use `MetadataMixin` only for flexible non-query-critical data
- use `VersionMixin` on editorial aggregates where optimistic locking is useful
- use `SlugMixin` for normalized identifiers, but enforce uniqueness at the model level only where the aggregate actually needs it

## Repository Rules

- repositories translate between SQLAlchemy models and domain entities
- repositories should return domain objects, not ORM models
- complex query behavior belongs here, not in routers or use cases

## Unit Of Work

`SqlAlchemyUnitOfWork` is the composition root for repository access inside transactional use cases. Any repository used from the application layer must be exposed there.

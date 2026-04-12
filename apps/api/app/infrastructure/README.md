# Infrastructure Layer

This folder contains adapters that connect the application to external systems.

## Current Progress

This layer already supports the current backend end to end:

- JWT auth, password hashing, OAuth integration, and session helpers
- Redis client management, cache wrappers, key helpers, and pub/sub support for book
  processing updates
- async SQLAlchemy persistence for the implemented aggregates
- local file storage for uploaded PDFs
- typed settings, DI helpers, logging, and startup/shutdown bootstrap

## Main Areas

- `auth/`: JWT, password hashing, OAuth integration, session caching helpers
- `cache/`: Redis client management, cache wrapper, and cache key helpers
- `config/`: strongly typed settings loaded from environment variables
- `di/`: reusable FastAPI dependency aliases and shared imports
- `logging/`: Loguru setup and logger access
- `persistence/`: async SQLAlchemy engine, models, repositories, pagination, unit of
  work
- `storage/`: file storage abstraction and current local filesystem implementation
- `bootstrap.py`: startup and shutdown orchestration

## Reusable Files In This Folder

- `bootstrap.py`: creates storage directories, configures logging, initializes DB and
  Redis, and closes them on shutdown
- `config/settings.py`: the single source of truth for environment configuration
- `di/dependencies.py`: typed aliases such as `UnitOfWorkDep`, `DatabaseSession`, and
  `CacheDep`
- `logging/logger.py`: logging setup used across the service

## Rules

- keep framework and external-system code here
- convert external representations into domain or application-facing abstractions
- do not move business rules out of the domain just because the data comes from
  Postgres, Redis, or file storage

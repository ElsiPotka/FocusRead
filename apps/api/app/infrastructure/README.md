# Infrastructure Layer

This folder contains adapters that connect the application to external systems.

## Main Areas

- `auth/`: JWT, password hashing, OAuth integration, session caching helpers
- `cache/`: Redis client management, cache wrapper, cache key helpers
- `config/`: strongly-typed settings loaded from environment variables
- `di/`: reusable FastAPI dependency aliases and shared imports
- `logging/`: Loguru setup and logger access
- `persistence/`: async SQLAlchemy engine, models, repositories, pagination, unit of work
- `bootstrap.py`: startup and shutdown orchestration

## Reusable Files In This Folder

- `bootstrap.py`: creates storage directories, configures logging, initializes DB and Redis, and closes them on shutdown
- `config/settings.py`: the single source of truth for environment configuration
- `di/dependencies.py`: typed aliases such as `UnitOfWorkDep`, `DatabaseSession`, and `CacheDep`
- `logging/logger.py`: logging setup used across the service

## Rules

- keep framework and external-system code here
- convert external representations into domain or application-facing abstractions
- do not move business rules out of the domain just because the data comes from Postgres or Redis

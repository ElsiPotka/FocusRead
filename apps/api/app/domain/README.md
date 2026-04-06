# Domain Layer

This folder contains the pure business model for the API.

## What Belongs Here

- entities
- value objects
- domain errors
- repository interfaces

## Rules

- keep the domain free of FastAPI, SQLAlchemy, Redis, and Pydantic
- encode validation in value objects where practical
- keep business invariants inside entities and domain services
- use repositories as interfaces only; infrastructure implements them

## Current Aggregates

- `books/`: book entities, status, repositories, and related rules
- `user/`: user entity
- `session/`: session entity
- `account/`: account entity
- `auth/`: auth-specific repository contracts, value objects, errors, and entity compatibility exports

`auth/entities/` currently acts as a compatibility facade. The concrete entity implementations live in the aggregate-specific folders such as `user/`, `session/`, and `account/`.

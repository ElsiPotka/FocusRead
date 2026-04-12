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

Auth and identity:

- `auth/`
- `user/`
- `session/`
- `account/`
- `role/`

Reading and library:

- `books/`
- `book_chunks/`
- `book_toc_entry/`
- `reading_sessions/`
- `reading_stats/`
- `user_book_state/`

Organization and curation:

- `bookmark/`
- `contributor/`
- `label/`
- `shelf/`

This means the domain layer already models the main backend concepts from the current
product idea: ingest, read, organize, measure, and curate.

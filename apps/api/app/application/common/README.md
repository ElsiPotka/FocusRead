# Application Common

Shared application-level contracts and errors live here.

## Files

- `errors.py`: application exceptions that are later mapped to HTTP responses
- `unit_of_work.py`: the application-facing transactional contract

## Current Progress

`AbstractUnitOfWork` is already the shared composition surface for the current backend
feature set. It exposes repositories for:

- books, book chunks, and TOC entries
- bookmarks, contributors, labels, shelves, and user book state
- reading sessions and reading stats
- users, roles, accounts, sessions, and JWT signing keys

## Unit Of Work Rules

When you add a repository-backed feature:

1. add the repository attribute to `AbstractUnitOfWork`
2. implement and wire that repository in
   `app/infrastructure/persistence/unit_of_work.py`
3. consume it from use cases through `self.uow.<repository_name>`

This keeps use cases decoupled from concrete database implementations while still
making transactional boundaries explicit.

# Tests

This folder contains automated tests for the API service.

## Current Structure

- `domain/`: unit tests for entities and value objects
- `usecase/`: application use-case tests with mocked repositories and services

## Existing Test Style

- domain tests instantiate entities and value objects directly
- use-case tests mock repository interfaces with `AsyncMock`
- use-case tests usually mock `AbstractUnitOfWork` instead of using a real database session

## When Adding A Feature

Add tests in the matching slice:

- `tests/domain/<feature>/` for value objects and entities
- `tests/usecase/<feature>/` for application workflows

If you later add API or repository integration tests, create dedicated folders such as:

- `tests/presentation/`
- `tests/integration/`

Keep layer boundaries in tests as strict as in the application code.

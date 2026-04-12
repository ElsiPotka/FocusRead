# Tests

This folder contains automated tests for the API service.

## Current Structure

- `domain/`: unit tests for entities and value objects
- `usecase/`: application use-case tests with mocked repositories and services
- `presentation/`: router and authorization behavior tests
- `infrastructure/`: settings and persistence-helper tests
- `workers/`: tokenizer and worker-adjacent tests

## Current Coverage Shape

Most coverage is still concentrated where it gives the fastest signal:

- domain tests instantiate entities and value objects directly
- use-case tests mock repository interfaces with `AsyncMock`
- use-case tests usually mock `AbstractUnitOfWork` instead of using a real database
  session
- presentation tests exercise important route behavior such as books and admin access
- infrastructure and worker tests cover key helpers and low-level behavior

What is still relatively light:

- full database-backed repository integration tests
- Redis-backed integration tests
- end-to-end upload-to-worker processing tests

## When Adding A Feature

Add tests in the matching slice:

- `tests/domain/<feature>/` for value objects and entities
- `tests/usecase/<feature>/` for application workflows
- `tests/presentation/` for router behavior and auth/response contracts
- `tests/infrastructure/` or `tests/workers/` for adapter-specific logic

Keep layer boundaries in tests as strict as in the application code.

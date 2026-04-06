# Application Common

Shared application-level contracts and errors live here.

## Files

- `errors.py`: application exceptions that can be mapped to HTTP responses
- `unit_of_work.py`: the application-facing transactional contract

## Unit Of Work Rules

When you add a repository-backed feature:

1. add the repository attribute to `AbstractUnitOfWork`
2. implement and wire that repository in `app/infrastructure/persistence/unit_of_work.py`
3. consume it from use cases through `self.uow.<repository_name>`

This keeps use cases decoupled from concrete database implementations.

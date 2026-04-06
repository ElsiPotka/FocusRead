# App Package

`app/` contains the runtime code for the API service.

## Main Folders

- `application/`: use cases that coordinate domain logic and transactional work
- `domain/`: pure business logic, repository contracts, value objects, domain errors
- `infrastructure/`: external adapters such as SQLAlchemy, Redis, auth helpers, config, and logging
- `presentation/`: FastAPI routers, schemas, middleware, and exception handling
- `workers/`: Celery broker, scheduler, and async background tasks
- `main.py`: FastAPI application entrypoint

## Dependency Direction

The intended dependency flow is:

```text
presentation -> application -> domain
infrastructure -> domain
presentation -> infrastructure
application -> infrastructure only through shared application-facing contracts such as the unit of work
```

## Rule Of Thumb

When adding a feature, follow the slice in this order:

1. `domain`
2. `infrastructure/persistence`
3. `application`
4. `presentation`
5. `tests`

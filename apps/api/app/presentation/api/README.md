# API Package

This package contains the concrete FastAPI HTTP implementation.

## Files And Folders

- `routers/`: route modules registered into the application
- `schemas/`: Pydantic request and response models
- `middleware/`: middleware components such as auth helpers
- `middlewares.py`: central middleware registration
- `exception_handlers.py`: exception-to-response mapping

## Working In This Folder

When adding a new API feature:

1. add or update request and response schemas in `schemas/`
2. add the route module in `routers/`
3. register the router in `routers/__init__.py`
4. add shared dependencies only if they are reused broadly

Keep the router thin. It should parse the request, call a use case, and shape the response.

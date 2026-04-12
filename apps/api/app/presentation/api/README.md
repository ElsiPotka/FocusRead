# API Package

This package contains the concrete FastAPI HTTP implementation.

## Current API Surface

Routers currently cover:

- `health.py`: health check
- `auth.py`: register, login, refresh, logout, and OAuth callbacks
- `users.py`: current user profile
- `books.py`: upload, processing-status SSE, state preferences, chunk access, search,
  filtered book lists, metadata CRUD, and TOC retrieval
- `bookmarks.py`: bookmark CRUD
- `contributors.py`: contributor management in a book context
- `labels.py`: label CRUD plus label assignment to books
- `shelves.py`: shelf CRUD, shelf ordering, and shelf-book ordering
- `reading.py`: reading-session fetch and progress upsert
- `stats.py`: reading summary and per-book stats
- `admin.py`: user listing, role management, and system-label CRUD

## Files And Folders

- `routers/`: route modules registered into the application
- `schemas/`: Pydantic request and response models
- `middleware/`: middleware components such as auth, rate limiting, and request IDs
- `middlewares.py`: central middleware registration
- `exception_handlers.py`: exception-to-response mapping

## Working In This Folder

When adding a new API feature:

1. add or update request and response schemas in `schemas/`
2. add the route module in `routers/`
3. register the router in `routers/__init__.py`
4. add shared dependencies only if they are reused broadly

Keep the router thin. It should parse the request, call a use case, and shape the
response.

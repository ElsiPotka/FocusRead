# Application Layer

This folder contains use cases and application orchestration.

## Purpose

Application code coordinates workflows across repositories and services without
owning HTTP or ORM details.

## Current Progress

The application layer now covers the main FocusRead backend workflows:

- `admin/`: user listing, role assignment/removal, system-label CRUD
- `auth/`: registration, login, refresh, logout, current-user lookup, profile, OAuth
- `books/`: upload, list/get/update/delete, chunk fetch, chunk resolution, TOC read,
  and search
- `bookmarks/`: create, list, update, delete
- `contributors/`: attach, list, reorder, update, detach
- `labels/`: create, list, update, delete, assign, unassign
- `reading/`: reading-session fetch, progress upsert, summary stats, book stats
- `shelves/`: create, list, get, update, delete, reorder, and shelf-book operations
- `common/`: shared contracts and errors used across modules

## Rules

- accept primitives from callers and convert them into domain value objects
- talk to repositories through the unit of work
- commit explicitly at the transactional boundary
- do not import FastAPI `Request` or `Response` here
- do not return SQLAlchemy models from use cases

Most of the remaining backend work in this layer is extension and refinement, not new
foundational structure.

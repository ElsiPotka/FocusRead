# Presentation Layer

This folder contains the HTTP-facing FastAPI layer.

## Purpose

Presentation code validates HTTP input, invokes application use cases, and maps
results into API responses.

## Current Progress

The API surface is already broad enough to support the current backend product flows.
`api/` contains routers, schemas, middleware, and exception handlers for:

- health and meta routes
- auth and current-user routes
- books, chunk access, processing status SSE, and library discovery views
- bookmarks, contributors, labels, and shelves
- reading sessions and reading stats
- admin role management and system-label curation

## Rules

- keep HTTP concerns here: headers, cookies, status codes, query params, and request
  bodies
- map domain and application errors into HTTP responses here
- do not place persistence queries or business rules in routers

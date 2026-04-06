# Presentation Layer

This folder contains the HTTP-facing FastAPI layer.

## Purpose

Presentation code validates HTTP input, invokes application use cases, and maps results into API responses.

## Current Contents

- `api/`: routers, schemas, middleware, and exception handlers

## Rules

- keep HTTP concerns here: headers, cookies, status codes, query params, request bodies
- map domain and application errors into HTTP responses here
- do not place persistence queries or business rules in routers

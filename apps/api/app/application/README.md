# Application Layer

This folder contains use cases and application orchestration.

## Purpose

Application code coordinates workflows across repositories and services without owning HTTP or ORM details.

## What Belongs Here

- feature-oriented use cases such as `auth/` and `books/`
- transaction boundaries through `AbstractUnitOfWork`
- application-level error mapping when needed

## Rules

- accept primitives from callers and convert them into domain value objects
- talk to repositories through the unit of work
- commit once after successful writes
- do not import FastAPI `Request` or `Response` here
- do not return SQLAlchemy models from use cases

## Current Structure

- `auth/`: registration, login, refresh, logout, and OAuth callback flows
- `books/`: book upload registration flow
- `common/`: shared contracts and errors used by multiple feature modules

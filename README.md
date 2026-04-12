# FocusRead

FocusRead is a mobile-first speed-reading product for uploaded PDFs. The product
direction lives in [docs/IDEA.md](docs/IDEA.md), and the backend rollout notes live
in [docs/BACKEND_IMPLEMENTATION_PLAN.md](docs/BACKEND_IMPLEMENTATION_PLAN.md).

## Monorepo

- `apps/api` - FastAPI backend and background processing pipeline
- `apps/web` - web/PWA client placeholder
- `apps/mobile` - Expo/React Native client placeholder
- `apps/deployment` - Docker Compose, Nginx, and PgBouncer bootstrap
- `packages/shared` - shared package placeholder
- `docs` - product and implementation documentation

## Project Progression

As of 2026-04-12:

- `apps/api` is the most complete part of the repo and already covers the core
  backend described in `docs/IDEA.md`: auth, PDF upload, async chunk processing, SSE
  processing updates, chunk retrieval, reading progress/statistics, user book state,
  shelves, labels, bookmarks, contributors, search, and admin curation flows.
- `docs/BACKEND_IMPLEMENTATION_PLAN.md` is effectively complete from a backend
  feature-planning perspective; the migrations, routes, workers, and tests for those
  phases are now in the codebase.
- `apps/web`, `apps/mobile`, and `packages/shared` are still mostly placeholders, so
  the remaining product work is primarily client implementation and end-to-end
  integration.
- `apps/deployment` now contains an initial container and proxy setup, but deployment
  hardening and runtime validation are still separate work.

## Current Position

The backend looks close to "done for v1" relative to the original idea. The biggest
remaining steps are:

- build the reading clients
- wire end-to-end flows across client, API, worker, and infra
- finish backend polish items that help reliability but are not blocking, such as
  broader integration coverage and any remaining enrichment or extraction work

## Start Here

- [docs/IDEA.md](docs/IDEA.md)
- [docs/BACKEND_IMPLEMENTATION_PLAN.md](docs/BACKEND_IMPLEMENTATION_PLAN.md)
- [apps/api/README.md](apps/api/README.md)

# Workers

This folder contains the Celery integration for background work.

## Current Progress

The worker layer is already responsible for the core async ingest pipeline:

- accept a queued book-processing task after upload
- parse PDFs with PyMuPDF
- tokenize extracted content into compact word/image tokens
- persist `book_chunks`
- cache hot chunks in Redis
- publish processing progress events over Redis for the SSE endpoint
- update final book status, counts, and image flags

Automatic TOC extraction is the main visible gap still left in this folder.

## Files

- `broker.py`: Celery app configuration
- `pdf_processor.py`: PyMuPDF chunk extraction pipeline
- `tokenizer.py`: compact token generation and pause-multiplier logic
- `task.py`: task implementations, status publishing, and persistence orchestration
- `scheduler.py`: scheduled task registration

## Notes

- the Celery app reads broker and backend settings from
  `app.infrastructure.config.settings`
- persistence models are imported during worker boot so SQLAlchemy metadata is
  available consistently
- keep long-running or asynchronous background workflows here instead of inside HTTP
  request handlers

Run a worker from `apps/api`:

```bash
uv run celery -A app.workers.broker.celery_app worker --loglevel=info
```

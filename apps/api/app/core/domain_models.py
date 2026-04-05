"""Central registry for SQLAlchemy models.

Import every ORM model here so:
- Alembic can discover metadata without editing `alembic/env.py` repeatedly
- model modules are imported during app startup
"""

from app.infrastructure.persistence.models.book import BookModel

__all__ = ["BookModel"]

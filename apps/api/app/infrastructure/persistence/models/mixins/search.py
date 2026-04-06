from typing import ClassVar

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column


class SearchMixin:
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        nullable=True,
        deferred=True,
        comment="Full-text search vector",
    )

    __searchable_fields__: ClassVar[list[str]] = []

    @classmethod
    def search_criteria(cls, query: str, language: str = "english"):
        return cls.search_vector.op("@@")(func.plainto_tsquery(language, query))

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.infrastructure.persistence.models.book import BookModel

if TYPE_CHECKING:
    from sqlalchemy import Table


def test_book_search_vector_is_generated_and_indexed() -> None:
    table = cast("Table", BookModel.__table__)
    ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))

    assert "search_vector TSVECTOR GENERATED ALWAYS AS (" in ddl
    assert "to_tsvector('pg_catalog.english'::regconfig" in ddl
    assert "coalesce(\"title\"::text, '')" in ddl
    assert "coalesce(\"source_filename\"::text, '')" in ddl
    assert "STORED NOT NULL" in ddl

    search_index = next(
        index for index in table.indexes if index.name == "ix_books_search_vector"
    )
    assert search_index.dialect_options["postgresql"]["using"] == "gin"

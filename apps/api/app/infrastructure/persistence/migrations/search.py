from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.infrastructure.persistence.models.mixins.search import (
    search_vector_generated_sql,
    search_vector_index_name,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_identifier(value: str, *, kind: str) -> str:
    if not _IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid {kind}: {value!r}")
    return value


def search_vector_column(
    *,
    searchable_columns: Sequence[str],
    language: str = "english",
    column_name: str = "search_vector",
) -> sa.Column[Any]:
    column = _validate_identifier(column_name, kind="column name")
    return sa.Column(
        column,
        TSVECTOR(),
        sa.Computed(
            search_vector_generated_sql(searchable_columns, language=language),
            persisted=True,
        ),
        nullable=False,
    )


def create_search_vector_index(
    op: Any,
    *,
    table_name: str,
    column_name: str = "search_vector",
) -> None:
    table = _validate_identifier(table_name, kind="table name")
    column = _validate_identifier(column_name, kind="column name")
    op.create_index(
        search_vector_index_name(table, column_name=column),
        table,
        [column],
        unique=False,
        postgresql_using="gin",
    )


def drop_search_vector_index(
    op: Any,
    *,
    table_name: str,
    column_name: str = "search_vector",
) -> None:
    table = _validate_identifier(table_name, kind="table name")
    column = _validate_identifier(column_name, kind="column name")
    op.drop_index(search_vector_index_name(table, column_name=column), table_name=table)

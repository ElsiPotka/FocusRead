from __future__ import annotations

import re
from typing import TYPE_CHECKING, Protocol, cast

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.infrastructure.persistence.models.mixins.search import (
    search_vector_generated_sql,
    search_vector_index_name,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class _AlembicOpLike(Protocol):
    def create_index(
        self,
        index_name: str,
        table_name: str,
        columns: list[str],
        *,
        unique: bool = False,
        postgresql_using: str | None = None,
    ) -> None: ...

    def drop_index(
        self,
        index_name: str,
        *,
        table_name: str | None = None,
    ) -> None: ...


def _validate_identifier(value: str, *, kind: str) -> str:
    if not _IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid {kind}: {value!r}")
    return value


def search_vector_column(
    *,
    searchable_columns: Sequence[str],
    language: str = "english",
    column_name: str = "search_vector",
) -> sa.Column[str]:
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
    op: object,
    *,
    table_name: str,
    column_name: str = "search_vector",
) -> None:
    alembic_op = cast("_AlembicOpLike", op)
    table = _validate_identifier(table_name, kind="table name")
    column = _validate_identifier(column_name, kind="column name")
    alembic_op.create_index(
        search_vector_index_name(table, column_name=column),
        table,
        [column],
        unique=False,
        postgresql_using="gin",
    )


def drop_search_vector_index(
    op: object,
    *,
    table_name: str,
    column_name: str = "search_vector",
) -> None:
    alembic_op = cast("_AlembicOpLike", op)
    table = _validate_identifier(table_name, kind="table name")
    column = _validate_identifier(column_name, kind="column name")
    alembic_op.drop_index(
        search_vector_index_name(table, column_name=column),
        table_name=table,
    )

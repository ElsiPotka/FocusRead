from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

from sqlalchemy import Computed, Index, Text, cast, func, literal
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

if TYPE_CHECKING:
    from collections.abc import Sequence

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_identifier(value: str, *, kind: str) -> str:
    if not _IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid {kind}: {value!r}")
    return value


def _quoted_identifier(value: str, *, kind: str) -> str:
    return f'"{_validate_identifier(value, kind=kind)}"'


def search_language_config(language: str) -> str:
    normalized = _validate_identifier(language, kind="language")
    return f"pg_catalog.{normalized}"


def search_document_sql(searchable_fields: Sequence[str]) -> str:
    columns = [
        _quoted_identifier(column_name, kind="column name")
        for column_name in searchable_fields
    ]
    if not columns:
        raise ValueError("At least one searchable column is required.")
    return " || ' ' || ".join(
        f"coalesce({column_name}::text, '')" for column_name in columns
    )


def search_vector_generated_sql(
    searchable_fields: Sequence[str],
    *,
    language: str = "english",
) -> str:
    return (
        f"to_tsvector('{search_language_config(language)}'::regconfig, "
        f"{search_document_sql(searchable_fields)})"
    )


def search_vector_index_name(
    table_name: str,
    *,
    column_name: str = "search_vector",
) -> str:
    return f"ix_{table_name}_{column_name}"


def search_vector_index(
    table_name: str,
    *,
    column_name: str = "search_vector",
) -> Index:
    return Index(
        search_vector_index_name(table_name, column_name=column_name),
        column_name,
        postgresql_using="gin",
    )


class SearchMixin:
    """Adds a PostgreSQL full-text search vector and query helper."""

    __tablename__: ClassVar[str]
    __searchable_fields__: ClassVar[tuple[str, ...]] = ()
    __search_language__: ClassVar[str] = "english"

    @declared_attr
    def search_vector(cls) -> Mapped[str]:
        return mapped_column(
            TSVECTOR,
            Computed(
                search_vector_generated_sql(
                    cls.__searchable_fields__,
                    language=cls.__search_language__,
                ),
                persisted=True,
            ),
            nullable=False,
            deferred=True,
            comment="Full-text search vector",
        )

    @classmethod
    def build_search_document_expression(cls):
        if not cls.__searchable_fields__:
            raise ValueError(f"{cls.__name__} must define __searchable_fields__.")

        searchable_fields = iter(cls.__searchable_fields__)
        first_field = next(searchable_fields)
        document = func.coalesce(cast(getattr(cls, first_field), Text), literal(""))
        for field_name in searchable_fields:
            document = (
                document
                + literal(" ")
                + func.coalesce(cast(getattr(cls, field_name), Text), literal(""))
            )
        return document

    @classmethod
    def build_search_vector_expression(cls):
        return func.to_tsvector(
            cls.__search_language__,
            cls.build_search_document_expression(),
        )

    @classmethod
    def search_criteria(cls, query: str, language: str | None = None):
        return cls.search_vector.op("@@")(
            func.plainto_tsquery(language or cls.__search_language__, query)
        )

    @classmethod
    def search_index_name(cls) -> str:
        return search_vector_index_name(cls.__tablename__)

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import flag_modified

from app.types import JSONObject  # noqa: TC001

if TYPE_CHECKING:
    from app.types import JSONValue


class MetadataMixin:
    """Adds mutable JSON metadata helpers to a persistence model."""

    entity_metadata: Mapped[JSONObject | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Flexible JSON metadata storage",
    )

    def set_metadata(self, key: str, value: JSONValue) -> None:
        metadata = self.entity_metadata
        if metadata is None:
            metadata = {}
            self.entity_metadata = metadata
        metadata[key] = value
        flag_modified(self, "entity_metadata")

    def get_metadata[TDefault](
        self, key: str, default: TDefault | None = None
    ) -> JSONValue | TDefault | None:
        if self.entity_metadata is None:
            return default
        return self.entity_metadata.get(key, default)

    def remove_metadata(self, key: str) -> None:
        if self.entity_metadata and key in self.entity_metadata:
            del self.entity_metadata[key]
            flag_modified(self, "entity_metadata")

from __future__ import annotations

from typing import Any, cast

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.attributes import flag_modified


class MetadataMixin:
    entity_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Flexible JSON metadata storage",
    )

    def set_metadata(self, key: str, value: Any) -> None:
        if self.entity_metadata is None:
            self.entity_metadata = {}

        metadata = cast("dict[str, Any]", self.entity_metadata)
        metadata[key] = value
        flag_modified(self, "entity_metadata")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        if self.entity_metadata is None:
            return default
        return self.entity_metadata.get(key, default)

    def remove_metadata(self, key: str) -> None:
        if self.entity_metadata and key in self.entity_metadata:
            del self.entity_metadata[key]
            flag_modified(self, "entity_metadata")

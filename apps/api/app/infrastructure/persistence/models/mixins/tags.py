from typing import cast

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column


class TagsMixin:
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
        comment="Array of tags",
    )

    def add_tag(self, tag: str) -> None:
        if self.tags is None:
            self.tags = []

        tags_list = cast("list[str]", self.tags)
        if tag not in tags_list:
            tags_list.append(tag)

    def remove_tag(self, tag: str) -> None:
        if self.tags and tag in self.tags:
            self.tags.remove(tag)

    def has_tag(self, tag: str) -> bool:
        return self.tags is not None and tag in self.tags

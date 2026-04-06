import re
from typing import ClassVar

from sqlalchemy import String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class SlugMixin:
    """Adds a slug column and normalized slug generator."""

    __slug_nullable__: ClassVar[bool] = True

    @declared_attr
    def slug(cls) -> Mapped[str | None]:
        return mapped_column(
            String(255),
            nullable=cls.__slug_nullable__,
            comment="URL-friendly identifier",
        )

    @staticmethod
    def generate_slug(title: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

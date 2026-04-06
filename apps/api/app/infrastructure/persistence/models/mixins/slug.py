import re

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class SlugMixin:
    slug: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        comment="URL-friendly identifier",
    )

    @staticmethod
    def generate_slug(title: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

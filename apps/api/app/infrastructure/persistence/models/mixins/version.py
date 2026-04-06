from sqlalchemy import Integer, text
from sqlalchemy.orm import Mapped, mapped_column


class VersionMixin:
    """Adds an optimistic-lock version column for concurrent updates."""

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
        comment="Version for optimistic locking",
    )

    __mapper_args__ = {"version_id_col": version}

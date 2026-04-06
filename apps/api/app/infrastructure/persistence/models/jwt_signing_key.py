from datetime import datetime  # noqa: TC003

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.models.base_model import BaseModel


class JWTSigningKeyModel(BaseModel):
    __tablename__ = "jwt_signing_keys"

    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    private_key: Mapped[str] = mapped_column(Text, nullable=False)
    algorithm: Mapped[str] = mapped_column(
        String(10), nullable=False, default="RS256", server_default="RS256"
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index(
            "ix_jwt_signing_keys_active",
            "id",
            unique=True,
            postgresql_where=expires_at.is_(None),
        ),
    )

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, computed_field

if TYPE_CHECKING:
    from datetime import datetime


class SoftDeleteMixin(BaseModel):
    """Exposes soft-delete timestamps and derived flags on API schemas."""

    deleted_at: datetime | None = Field(
        default=None, description="Soft delete timestamp"
    )

    @computed_field
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @computed_field
    @property
    def is_active(self) -> bool:
        return self.deleted_at is None

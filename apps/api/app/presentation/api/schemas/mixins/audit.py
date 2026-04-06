from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    import uuid


class AuditMixin(BaseModel):
    created_by: uuid.UUID | None = Field(
        default=None, description="User who created this record"
    )
    updated_by: uuid.UUID | None = Field(
        default=None, description="User who last updated this record"
    )
    deleted_by: uuid.UUID | None = Field(
        default=None, description="User who soft-deleted this record"
    )

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.domain.label.entities import Label


class LabelResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    color: str | None
    is_system: bool
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(label: Label) -> LabelResponse:
        return LabelResponse(
            id=label.id.value,
            name=label.name.value,
            slug=label.slug.value,
            color=label.color.value if label.color else None,
            is_system=label.is_system,
            created_at=label.created_at,
            updated_at=label.updated_at,
        )


class CreateLabelRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    color: str | None = Field(None, max_length=32)


class UpdateLabelRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    color: str | None = Field(None, max_length=32)
    clear_color: bool = False


class AssignLabelRequest(BaseModel):
    label_id: UUID

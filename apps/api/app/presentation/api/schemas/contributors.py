from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.domain.contributor.entities import Contributor
    from app.domain.contributor.value_objects import ContributorRole


class ContributorResponse(BaseModel):
    id: UUID
    display_name: str
    sort_name: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(contributor: Contributor) -> ContributorResponse:
        return ContributorResponse(
            id=contributor.id.value,
            display_name=contributor.display_name.value,
            sort_name=contributor.sort_name.value if contributor.sort_name else None,
            created_at=contributor.created_at,
            updated_at=contributor.updated_at,
        )


class BookContributorResponse(BaseModel):
    contributor: ContributorResponse
    role: str
    position: int

    @staticmethod
    def from_tuple(
        data: tuple[Contributor, ContributorRole, int],
    ) -> BookContributorResponse:
        contributor, role, position = data
        return BookContributorResponse(
            contributor=ContributorResponse.from_entity(contributor),
            role=role.value,
            position=position,
        )


class AttachContributorRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)
    sort_name: str | None = Field(None, max_length=255)
    role: str = Field(default="author")


class ReorderItem(BaseModel):
    contributor_id: UUID
    role: str
    position: int = Field(..., ge=0)


class ReorderContributorsRequest(BaseModel):
    ordering: list[ReorderItem]

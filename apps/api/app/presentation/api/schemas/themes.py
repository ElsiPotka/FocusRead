from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.domain.theme.entities import Theme


class ThemeResponse(BaseModel):
    """Theme metadata (no tokens) for marketplace browse."""

    id: UUID
    name: str
    slug: str
    description: str | None
    owner_user_id: UUID | None
    preview_image_url: str | None
    tags: list[str] | None
    is_public: bool
    is_system: bool
    is_featured: bool
    download_count: int
    like_count: int
    forked_from_id: UUID | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(theme: Theme) -> ThemeResponse:
        return ThemeResponse(
            id=theme.id.value,
            name=theme.name.value,
            slug=theme.slug.value,
            description=theme.description.value if theme.description else None,
            owner_user_id=theme.owner_user_id.value if theme.owner_user_id else None,
            preview_image_url=theme.preview_image_url,
            tags=theme.tags,
            is_public=theme.is_public,
            is_system=theme.is_system,
            is_featured=theme.is_featured,
            download_count=theme.download_count,
            like_count=theme.like_count,
            forked_from_id=theme.forked_from_id.value if theme.forked_from_id else None,
            created_at=theme.created_at,
            updated_at=theme.updated_at,
        )


class ThemeDetailResponse(ThemeResponse):
    """Full theme with tokens for preview/editing."""

    tokens: dict[str, str]

    @staticmethod
    def from_entity(theme: Theme) -> ThemeDetailResponse:  # type: ignore[override]
        return ThemeDetailResponse(
            id=theme.id.value,
            name=theme.name.value,
            slug=theme.slug.value,
            description=theme.description.value if theme.description else None,
            owner_user_id=theme.owner_user_id.value if theme.owner_user_id else None,
            preview_image_url=theme.preview_image_url,
            tags=theme.tags,
            is_public=theme.is_public,
            is_system=theme.is_system,
            is_featured=theme.is_featured,
            download_count=theme.download_count,
            like_count=theme.like_count,
            forked_from_id=theme.forked_from_id.value if theme.forked_from_id else None,
            created_at=theme.created_at,
            updated_at=theme.updated_at,
            tokens=theme.tokens.value,
        )


class ThemeTokensResponse(BaseModel):
    """Flat token map for the active theme hot path."""

    tokens: dict[str, str]


class CreateThemeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    tokens: dict[str, str]
    tags: list[str] | None = None


class UpdateThemeRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    tokens: dict[str, str] | None = None
    tags: list[str] | None = None


class ApplyThemeRequest(BaseModel):
    theme_id: UUID

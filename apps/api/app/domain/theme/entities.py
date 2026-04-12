from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.domain.theme.value_objects import (
    ThemeDescription,
    ThemeId,
    ThemeName,
    ThemeSlug,
    ThemeTokens,
)

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId


class ThemeError(Exception):
    pass


class Theme:
    def __init__(
        self,
        *,
        id: ThemeId,
        name: ThemeName,
        slug: ThemeSlug,
        tokens: ThemeTokens,
        owner_user_id: UserId | None = None,
        description: ThemeDescription | None = None,
        preview_image_url: str | None = None,
        tags: list[str] | None = None,
        is_public: bool = False,
        is_system: bool = False,
        is_featured: bool = False,
        download_count: int = 0,
        like_count: int = 0,
        forked_from_id: ThemeId | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._name = name
        self._slug = slug
        self._tokens = tokens
        self._owner_user_id = owner_user_id
        self._description = description
        self._preview_image_url = preview_image_url
        self._tags = tags
        self._is_public = is_public
        self._is_system = is_system
        self._is_featured = is_featured
        self._download_count = download_count
        self._like_count = like_count
        self._forked_from_id = forked_from_id
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        name: ThemeName,
        slug: ThemeSlug,
        tokens: ThemeTokens,
        owner_user_id: UserId | None = None,
        description: ThemeDescription | None = None,
        preview_image_url: str | None = None,
        tags: list[str] | None = None,
        forked_from_id: ThemeId | None = None,
    ) -> Theme:
        return cls(
            id=ThemeId.generate(),
            name=name,
            slug=slug,
            tokens=tokens,
            owner_user_id=owner_user_id,
            description=description,
            preview_image_url=preview_image_url,
            tags=tags,
            forked_from_id=forked_from_id,
        )

    # ── Properties ──

    @property
    def id(self) -> ThemeId:
        return self._id

    @property
    def name(self) -> ThemeName:
        return self._name

    @property
    def slug(self) -> ThemeSlug:
        return self._slug

    @property
    def tokens(self) -> ThemeTokens:
        return self._tokens

    @property
    def owner_user_id(self) -> UserId | None:
        return self._owner_user_id

    @property
    def description(self) -> ThemeDescription | None:
        return self._description

    @property
    def preview_image_url(self) -> str | None:
        return self._preview_image_url

    @property
    def tags(self) -> list[str] | None:
        return self._tags

    @property
    def is_public(self) -> bool:
        return self._is_public

    @property
    def is_system(self) -> bool:
        return self._is_system

    @property
    def is_featured(self) -> bool:
        return self._is_featured

    @property
    def download_count(self) -> int:
        return self._download_count

    @property
    def like_count(self) -> int:
        return self._like_count

    @property
    def forked_from_id(self) -> ThemeId | None:
        return self._forked_from_id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # ── Domain Methods ──

    def rename(
        self,
        *,
        name: ThemeName,
        slug: ThemeSlug,
        description: ThemeDescription | None = None,
    ) -> None:
        self.guard_not_system()
        self._name = name
        self._slug = slug
        self._description = description
        self._updated_at = datetime.now(UTC)

    def update_tokens(self, tokens: ThemeTokens) -> None:
        self.guard_not_system()
        self._tokens = tokens
        self._updated_at = datetime.now(UTC)

    def update_tags(self, tags: list[str] | None) -> None:
        self.guard_not_system()
        self._tags = tags
        self._updated_at = datetime.now(UTC)

    def update_preview(self, preview_image_url: str | None) -> None:
        self._preview_image_url = preview_image_url
        self._updated_at = datetime.now(UTC)

    def publish(self) -> None:
        self._is_public = True
        self._updated_at = datetime.now(UTC)

    def unpublish(self) -> None:
        self._is_public = False
        self._updated_at = datetime.now(UTC)

    def feature(self) -> None:
        self._is_featured = True
        self._updated_at = datetime.now(UTC)

    def unfeature(self) -> None:
        self._is_featured = False
        self._updated_at = datetime.now(UTC)

    def increment_downloads(self) -> None:
        self._download_count += 1

    def increment_likes(self) -> None:
        self._like_count += 1

    def decrement_likes(self) -> None:
        if self._like_count > 0:
            self._like_count -= 1

    def guard_not_system(self) -> None:
        if self._is_system:
            raise ThemeError("System themes cannot be modified.")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Theme) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

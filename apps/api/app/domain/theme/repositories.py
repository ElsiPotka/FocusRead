from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.theme.entities import Theme
    from app.domain.theme.value_objects import ThemeId, ThemeSlug


class ThemeRepository(ABC):
    @abstractmethod
    async def save(self, theme: Theme) -> None: ...

    @abstractmethod
    async def get(self, theme_id: ThemeId) -> Theme | None: ...

    @abstractmethod
    async def get_by_slug(self, *, slug: ThemeSlug) -> Theme | None: ...

    @abstractmethod
    async def get_for_owner(
        self, *, theme_id: ThemeId, user_id: UserId
    ) -> Theme | None: ...

    @abstractmethod
    async def list_for_user(self, *, user_id: UserId) -> list[Theme]: ...

    @abstractmethod
    async def list_public(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "popular",
        query: str | None = None,
    ) -> tuple[list[Theme], int]: ...

    @abstractmethod
    async def delete(self, theme_id: ThemeId) -> None: ...

    # ── User active theme ──

    @abstractmethod
    async def get_active_theme_id(self, *, user_id: UserId) -> ThemeId | None: ...

    @abstractmethod
    async def set_active_theme(self, *, user_id: UserId, theme_id: ThemeId) -> None: ...

    # ── Likes ──

    @abstractmethod
    async def has_user_liked(self, *, user_id: UserId, theme_id: ThemeId) -> bool: ...

    @abstractmethod
    async def add_like(self, *, user_id: UserId, theme_id: ThemeId) -> None: ...

    @abstractmethod
    async def remove_like(self, *, user_id: UserId, theme_id: ThemeId) -> None: ...

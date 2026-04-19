from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.theme.value_objects import ThemeId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class LikeTheme:
    """Toggle like: if already liked, unlikes; otherwise likes."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, *, theme_id: UUID, user_id: UUID) -> bool:
        """Returns True if liked, False if unliked."""
        tid = ThemeId(theme_id)
        uid = UserId(user_id)

        theme = await self._uow.themes.get(tid)
        if theme is None:
            raise NotFoundError("Theme not found")

        already_liked = await self._uow.themes.has_user_liked(user_id=uid, theme_id=tid)

        if already_liked:
            await self._uow.themes.remove_like(user_id=uid, theme_id=tid)
            await self._uow.commit()
            return False

        await self._uow.themes.add_like(user_id=uid, theme_id=tid)
        await self._uow.commit()
        return True

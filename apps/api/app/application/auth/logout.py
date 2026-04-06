from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.errors import InvalidRefreshTokenError
from app.domain.auth.value_objects import RefreshTokenHash

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.auth.session_service import SessionService


class LogoutUser:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        session_service: SessionService,
    ) -> None:
        self._uow = uow
        self._session_svc = session_service

    async def execute(self, *, raw_refresh_token: str) -> None:
        token_hash = self._session_svc.hash_token(raw_refresh_token)
        auth_session = await self._uow.sessions.get_by_token_hash(
            RefreshTokenHash(token_hash)
        )

        if auth_session is None:
            raise InvalidRefreshTokenError

        await self._uow.sessions.delete(auth_session.id)
        await self._uow.commit()

        await self._session_svc.invalidate_cached_session(token_hash)
        await self._session_svc.invalidate_current_user(str(auth_session.user_id.value))

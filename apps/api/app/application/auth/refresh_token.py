from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.application.auth.scopes import build_access_token_scopes
from app.domain.auth.errors import (
    InactiveUserError,
    InvalidRefreshTokenError,
    SessionExpiredError,
)
from app.domain.auth.value_objects import RefreshTokenHash
from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.auth.entities import User
    from app.infrastructure.auth.jwt_service import JWTService
    from app.infrastructure.auth.session_service import SessionService


class RefreshAccessToken:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        jwt_service: JWTService,
        session_service: SessionService,
    ) -> None:
        self._uow = uow
        self._jwt = jwt_service
        self._session_svc = session_service

    async def execute(
        self,
        *,
        raw_refresh_token: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        old_hash = self._session_svc.hash_token(raw_refresh_token)
        auth_session = await self._uow.sessions.get_by_token_hash(
            RefreshTokenHash(old_hash)
        )

        if auth_session is None:
            raise InvalidRefreshTokenError

        if auth_session.is_expired:
            await self._uow.sessions.delete(auth_session.id)
            await self._uow.commit()
            await self._session_svc.invalidate_cached_session(old_hash)
            raise SessionExpiredError

        user = await self._uow.users.get(auth_session.user_id)
        if user is None:
            raise InvalidRefreshTokenError

        if not user.is_active:
            raise InactiveUserError

        new_raw_refresh = self._session_svc.generate_refresh_token()
        new_hash = self._session_svc.hash_token(new_raw_refresh)
        new_expires = datetime.now(UTC) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

        auth_session.rotate(RefreshTokenHash(new_hash), new_expires)
        await self._uow.sessions.save(auth_session)

        roles = await self._uow.roles.list_for_user(user.id)
        private_key, _ = await self._jwt.get_or_create_key_pair(self._uow)
        access_token = self._jwt.encode_access_token(
            str(user.id.value),
            private_key,
            scopes=build_access_token_scopes(roles),
        )

        await self._uow.commit()

        await self._session_svc.invalidate_cached_session(old_hash)
        await self._session_svc.cache_session(new_hash, str(auth_session.id.value))
        await self._session_svc.invalidate_current_user(str(user.id.value))

        return (user, access_token, new_raw_refresh)

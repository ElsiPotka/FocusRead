from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.application.auth.scopes import build_access_token_scopes
from app.application.common.errors import NotFoundError
from app.domain.auth.entities import Session
from app.domain.auth.value_objects import Email, RefreshTokenHash, UserId
from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.user.entities import User
    from app.infrastructure.auth.jwt_service import JWTService
    from app.infrastructure.auth.session_service import SessionService


class ImpersonateUser:
    """Generate access + refresh tokens for a target user (admin only).

    The created session is a normal session — the impersonating admin
    can do anything the target user can do.  Audit callers externally.
    """

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
        user_id: UUID | None = None,
        email: str | None = None,
    ) -> tuple[User, str, str]:
        if user_id is None and email is None:
            raise NotFoundError("Provide either user_id or email")

        if user_id is not None:
            user = await self._uow.users.get(UserId(user_id))
        else:
            user = await self._uow.users.get_by_email(Email(email))  # type: ignore[arg-type]

        if user is None:
            raise NotFoundError("User not found")

        raw_refresh = self._session_svc.generate_refresh_token()
        token_hash = self._session_svc.hash_token(raw_refresh)
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
        )
        session = Session.create(
            user_id=user.id,
            token_hash=RefreshTokenHash(token_hash),
            expires_at=expires_at,
            user_agent="admin-impersonate",
            ip_address=None,
        )
        await self._uow.sessions.save(session)

        roles = await self._uow.roles.list_for_user(user.id)
        private_key, _ = await self._jwt.get_or_create_key_pair(self._uow)
        access_token = self._jwt.encode_access_token(
            str(user.id.value),
            private_key,
            scopes=build_access_token_scopes(roles),
        )

        await self._uow.commit()
        await self._session_svc.cache_session(token_hash, str(session.id.value))

        return (user, access_token, raw_refresh)

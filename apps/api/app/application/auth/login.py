from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.application.auth.scopes import build_access_token_scopes
from app.domain.auth.entities import Session, User
from app.domain.auth.errors import InactiveUserError, InvalidCredentialsError
from app.domain.auth.value_objects import Email, RefreshTokenHash
from app.infrastructure.auth.password import dummy_verify, verify_password
from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.auth.jwt_service import JWTService
    from app.infrastructure.auth.session_service import SessionService


class LoginUser:
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
        email: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        email_vo = Email(email)
        user = await self._uow.users.get_by_email(email_vo)

        if user is None:
            await dummy_verify()
            raise InvalidCredentialsError

        if not user.is_active:
            raise InactiveUserError

        account = await self._uow.accounts.get_credential_by_user(user.id)
        if account is None or account.hashed_password is None:
            await dummy_verify()
            raise InvalidCredentialsError

        valid = await verify_password(password, account.hashed_password.value)
        if not valid:
            raise InvalidCredentialsError

        raw_refresh = self._session_svc.generate_refresh_token()
        token_hash = self._session_svc.hash_token(raw_refresh)
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        auth_session = Session.create(
            user_id=user.id,
            token_hash=RefreshTokenHash(token_hash),
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        await self._uow.sessions.save(auth_session)

        roles = await self._uow.roles.list_for_user(user.id)
        private_key, _ = await self._jwt.get_or_create_key_pair(self._uow)
        access_token = self._jwt.encode_access_token(
            str(user.id.value),
            private_key,
            scopes=build_access_token_scopes(roles),
        )

        await self._uow.commit()

        await self._session_svc.cache_session(token_hash, str(auth_session.id.value))

        return (user, access_token, raw_refresh)

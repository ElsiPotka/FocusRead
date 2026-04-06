from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.domain.auth.entities import Account, Session, User
from app.domain.auth.errors import EmailAlreadyExistsError
from app.domain.auth.value_objects import Email, HashedPassword, RefreshTokenHash
from app.infrastructure.auth.password import hash_password
from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.auth.jwt_service import JWTService
    from app.infrastructure.auth.session_service import SessionService


class RegisterUser:
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
        name: str,
        surname: str,
        email: str,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        email_vo = Email(email)

        existing = await self._uow.users.get_by_email(email_vo)
        if existing is not None:
            raise EmailAlreadyExistsError

        user = User.create(name=name, surname=surname, email=email_vo)

        hashed = await hash_password(password)
        account = Account.create_credential(
            user_id=user.id,
            email=email_vo,
            hashed_password=HashedPassword(hashed),
        )

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

        await self._uow.users.save(user)
        await self._uow.accounts.save(account)
        await self._uow.sessions.save(auth_session)

        private_key, _ = await self._jwt.get_or_create_key_pair(self._uow)
        access_token = self._jwt.encode_access_token(str(user.id.value), private_key)

        await self._uow.commit()

        await self._session_svc.cache_session(token_hash, str(auth_session.id.value))

        return (user, access_token, raw_refresh)

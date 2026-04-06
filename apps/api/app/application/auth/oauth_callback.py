from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from app.application.auth.scopes import build_access_token_scopes
from app.domain.auth.entities import Account, Session, User
from app.domain.auth.value_objects import (
    AccountId,
    Email,
    ProviderId,
    RefreshTokenHash,
)
from app.domain.role.value_objects import RoleName
from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.domain.role.entities import Role
    from app.infrastructure.auth.jwt_service import JWTService
    from app.infrastructure.auth.session_service import SessionService


class HandleOAuthCallback:
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
        provider: str,
        oauth_user_info: dict[str, Any],
        oauth_tokens: dict[str, Any],
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        provider_id = ProviderId(provider)
        sub = oauth_user_info.get("sub") or oauth_user_info.get("id", "")
        email_str = oauth_user_info.get("email", "")
        name = oauth_user_info.get("given_name", oauth_user_info.get("name", ""))
        surname = oauth_user_info.get("family_name", "")
        roles: list[Role] = []

        existing_account = await self._uow.accounts.get_by_provider(provider_id, sub)

        if existing_account is not None:
            user = await self._uow.users.get(existing_account.user_id)
            if user is None:
                msg = "User not found for existing account"
                raise RuntimeError(msg)

            existing_account.update_oauth_tokens(
                access_token=oauth_tokens.get("access_token"),
                refresh_token=oauth_tokens.get("refresh_token"),
                id_token=oauth_tokens.get("id_token"),
                scope=oauth_tokens.get("scope"),
            )
            await self._uow.accounts.save(existing_account)
            roles = await self._uow.roles.list_for_user(user.id)
        else:
            email_vo = Email(email_str) if email_str else None
            user = None

            if email_vo is not None:
                user = await self._uow.users.get_by_email(email_vo)

            if user is None:
                user = User.create(
                    name=name,
                    surname=surname,
                    email=Email(email_str)
                    if email_str
                    else Email(f"{sub}@{provider}.oauth"),
                )
                user.verify_email()
                await self._uow.users.save(user)

                client_role = await self._uow.roles.get_by_name(RoleName.CLIENT)
                if client_role is None:
                    msg = "Default Client role is not configured."
                    raise RuntimeError(msg)
                await self._uow.roles.assign_to_user(user.id, client_role.id)
                roles = [client_role]
            else:
                roles = await self._uow.roles.list_for_user(user.id)

            account = Account.create_oauth(
                user_id=user.id,
                provider_id=provider_id,
                account_id=AccountId(sub),
                account_email=email_str or None,
                access_token=oauth_tokens.get("access_token"),
                refresh_token=oauth_tokens.get("refresh_token"),
                id_token=oauth_tokens.get("id_token"),
                scope=oauth_tokens.get("scope"),
            )
            await self._uow.accounts.save(account)

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

        private_key, _ = await self._jwt.get_or_create_key_pair(self._uow)
        access_token = self._jwt.encode_access_token(
            str(user.id.value),
            private_key,
            scopes=build_access_token_scopes(roles),
        )

        await self._uow.commit()

        await self._session_svc.cache_session(token_hash, str(auth_session.id.value))

        return (user, access_token, raw_refresh)

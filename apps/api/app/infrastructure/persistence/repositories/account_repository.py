from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.auth.entities import Account
from app.domain.auth.repositories import AccountRepository
from app.domain.auth.value_objects import (
    AccountId,
    HashedPassword,
    ProviderId,
    UserId,
)
from app.infrastructure.persistence.models.account import AccountModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyAccountRepository(AccountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, account: Account) -> None:
        model = await self.session.get(AccountModel, account.id.value)

        if model is None:
            model = AccountModel(
                id=account.id.value,
                user_id=account.user_id.value,
                provider_id=account.provider_id.value,
                account_id=account.account_id.value,
                account_email=account.account_email,
                password=account.hashed_password.value
                if account.hashed_password
                else None,
                access_token=account.access_token,
                refresh_token=account.refresh_token,
                access_token_expires_at=account.access_token_expires_at,
                refresh_token_expires_at=account.refresh_token_expires_at,
                id_token=account.id_token,
                scope=account.scope,
            )
            self.session.add(model)
            return

        model.account_email = account.account_email
        model.password = (
            account.hashed_password.value if account.hashed_password else None
        )
        model.access_token = account.access_token
        model.refresh_token = account.refresh_token
        model.access_token_expires_at = account.access_token_expires_at
        model.refresh_token_expires_at = account.refresh_token_expires_at
        model.id_token = account.id_token
        model.scope = account.scope

    async def get_by_provider(
        self, provider_id: ProviderId, account_id: str
    ) -> Account | None:
        stmt = select(AccountModel).where(
            AccountModel.provider_id == provider_id.value,
            AccountModel.account_id == account_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_credential_by_user(self, user_id: UserId) -> Account | None:
        stmt = select(AccountModel).where(
            AccountModel.user_id == user_id.value,
            AccountModel.provider_id == "credential",
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: AccountModel) -> Account:
        return Account(
            id=UserId(model.id),
            user_id=UserId(model.user_id),
            provider_id=ProviderId(model.provider_id),
            account_id=AccountId(model.account_id),
            account_email=model.account_email,
            hashed_password=HashedPassword(model.password) if model.password else None,
            access_token=model.access_token,
            refresh_token=model.refresh_token,
            access_token_expires_at=model.access_token_expires_at,
            refresh_token_expires_at=model.refresh_token_expires_at,
            id_token=model.id_token,
            scope=model.scope,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

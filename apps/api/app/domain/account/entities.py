from __future__ import annotations

from datetime import UTC, datetime

from app.domain.auth.value_objects import (
    AccountId,
    Email,
    HashedPassword,
    ProviderId,
    UserId,
)


class Account:
    def __init__(
        self,
        *,
        id: UserId,
        user_id: UserId,
        provider_id: ProviderId,
        account_id: AccountId,
        account_email: str | None = None,
        hashed_password: HashedPassword | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        access_token_expires_at: datetime | None = None,
        refresh_token_expires_at: datetime | None = None,
        id_token: str | None = None,
        scope: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._provider_id = provider_id
        self._account_id = account_id
        self._account_email = account_email
        self._hashed_password = hashed_password
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._access_token_expires_at = access_token_expires_at
        self._refresh_token_expires_at = refresh_token_expires_at
        self._id_token = id_token
        self._scope = scope
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create_credential(
        cls,
        *,
        user_id: UserId,
        email: Email,
        hashed_password: HashedPassword,
    ) -> Account:
        return cls(
            id=UserId.generate(),
            user_id=user_id,
            provider_id=ProviderId("credential"),
            account_id=AccountId(email.value),
            account_email=email.value,
            hashed_password=hashed_password,
        )

    @classmethod
    def create_oauth(
        cls,
        *,
        user_id: UserId,
        provider_id: ProviderId,
        account_id: AccountId,
        account_email: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        access_token_expires_at: datetime | None = None,
        refresh_token_expires_at: datetime | None = None,
        id_token: str | None = None,
        scope: str | None = None,
    ) -> Account:
        return cls(
            id=UserId.generate(),
            user_id=user_id,
            provider_id=provider_id,
            account_id=account_id,
            account_email=account_email,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_at=access_token_expires_at,
            refresh_token_expires_at=refresh_token_expires_at,
            id_token=id_token,
            scope=scope,
        )

    @property
    def id(self) -> UserId:
        return self._id

    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def provider_id(self) -> ProviderId:
        return self._provider_id

    @property
    def account_id(self) -> AccountId:
        return self._account_id

    @property
    def account_email(self) -> str | None:
        return self._account_email

    @property
    def hashed_password(self) -> HashedPassword | None:
        return self._hashed_password

    @property
    def access_token(self) -> str | None:
        return self._access_token

    @property
    def refresh_token(self) -> str | None:
        return self._refresh_token

    @property
    def access_token_expires_at(self) -> datetime | None:
        return self._access_token_expires_at

    @property
    def refresh_token_expires_at(self) -> datetime | None:
        return self._refresh_token_expires_at

    @property
    def id_token(self) -> str | None:
        return self._id_token

    @property
    def scope(self) -> str | None:
        return self._scope

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def update_oauth_tokens(
        self,
        *,
        access_token: str | None = None,
        refresh_token: str | None = None,
        access_token_expires_at: datetime | None = None,
        refresh_token_expires_at: datetime | None = None,
        id_token: str | None = None,
        scope: str | None = None,
    ) -> None:
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._access_token_expires_at = access_token_expires_at
        self._refresh_token_expires_at = refresh_token_expires_at
        self._id_token = id_token
        self._scope = scope
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Account) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

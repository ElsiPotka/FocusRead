from __future__ import annotations

import datetime as dt  # noqa: TC003
import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.domain.account.entities import Account
    from app.domain.user.entities import User


class LinkedAccountResponse(BaseModel):
    provider_id: str
    account_email: str | None
    created_at: dt.datetime

    @staticmethod
    def from_entity(account: Account) -> LinkedAccountResponse:
        return LinkedAccountResponse(
            provider_id=account.provider_id.value,
            account_email=account.account_email,
            created_at=account.created_at,
        )


class CurrentUserProfileResponse(BaseModel):
    id: uuid.UUID
    name: str
    surname: str
    email: str
    email_verified: bool
    image: str | None
    full_name: str
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime
    linked_accounts: list[LinkedAccountResponse]

    @staticmethod
    def from_entities(
        user: User,
        accounts: list[Account],
    ) -> CurrentUserProfileResponse:
        return CurrentUserProfileResponse(
            id=user.id.value,
            name=user.name,
            surname=user.surname,
            email=user.email.value,
            email_verified=user.email_verified,
            image=user.image,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            linked_accounts=[
                LinkedAccountResponse.from_entity(account)
                for account in sorted(accounts, key=lambda item: item.created_at)
            ],
        )

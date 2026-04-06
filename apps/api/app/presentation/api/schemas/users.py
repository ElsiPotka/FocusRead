from __future__ import annotations

import datetime as dt  # noqa: TC003
import uuid  # noqa: TC003
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.domain.account.entities import Account
    from app.domain.role.entities import Role
    from app.domain.user.entities import User
    from app.domain.user.profile import UserProfile


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


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str

    @staticmethod
    def from_entity(role: Role) -> RoleResponse:
        return RoleResponse(
            id=role.id.value,
            name=role.name.value,
            description=role.description,
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
    roles: list[RoleResponse]

    @staticmethod
    def from_entities(
        user: User,
        accounts: list[Account],
        roles: list[Role],
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
            roles=[
                RoleResponse.from_entity(role)
                for role in sorted(roles, key=lambda item: item.name.value)
            ],
        )

    @staticmethod
    def from_profile(profile: UserProfile) -> CurrentUserProfileResponse:
        return CurrentUserProfileResponse.from_entities(
            profile.user,
            list(profile.accounts),
            list(profile.roles),
        )


class AdminUserProfileResponse(CurrentUserProfileResponse):
    @staticmethod
    def from_profile(profile: UserProfile) -> AdminUserProfileResponse:
        return AdminUserProfileResponse.model_validate(
            CurrentUserProfileResponse.from_profile(profile)
        )


class UserRolesResponse(BaseModel):
    user_id: uuid.UUID
    roles: list[RoleResponse]

    @staticmethod
    def from_roles(user_id: uuid.UUID, roles: list[Role]) -> UserRolesResponse:
        return UserRolesResponse(
            user_id=user_id,
            roles=[
                RoleResponse.from_entity(role)
                for role in sorted(roles, key=lambda item: item.name.value)
            ],
        )

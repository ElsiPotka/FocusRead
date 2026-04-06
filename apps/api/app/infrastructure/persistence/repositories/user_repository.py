from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.domain.account.entities import Account
from app.domain.auth.entities import User
from app.domain.auth.repositories import UserRepository
from app.domain.auth.value_objects import (
    AccountId,
    Email,
    ProviderId,
    UserId,
)
from app.domain.role.entities import Role
from app.domain.role.value_objects import RoleId
from app.domain.user.profile import UserProfile
from app.infrastructure.persistence.models.account import AccountModel
from app.infrastructure.persistence.models.role import RoleModel
from app.infrastructure.persistence.models.user import UserModel
from app.infrastructure.persistence.pagination import paginate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, user: User) -> None:
        model = await self.session.get(UserModel, user.id.value)

        if model is None:
            model = UserModel(
                id=user.id.value,
                name=user.name,
                surname=user.surname,
                email=user.email.value,
                email_verified=user.email_verified,
                image=user.image,
                is_active=user.is_active,
            )
            self.session.add(model)
            return

        model.name = user.name
        model.surname = user.surname
        model.email = user.email.value
        model.email_verified = user.email_verified
        model.image = user.image
        model.is_active = user.is_active

    async def get(self, user_id: UserId) -> User | None:
        model = await self.session.get(UserModel, user_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(
            func.lower(UserModel.email) == email.value.lower()
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_profile(self, user_id: UserId) -> UserProfile | None:
        stmt = self._profile_select().where(UserModel.id == user_id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        return self._to_profile(model)

    async def paginate_profiles(
        self,
        *,
        page: int,
        per_page: int,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        result = await paginate(
            self.session,
            self._profile_select(),
            UserModel.id,
            page=page,
            per_page=per_page,
            cursor=cursor,
        )
        return {
            "items": [self._to_profile(model) for model in result["items"]],
            "meta": result["meta"],
        }

    @staticmethod
    def _profile_select():
        return select(UserModel).options(
            selectinload(UserModel.accounts).load_only(
                AccountModel.id,
                AccountModel.user_id,
                AccountModel.provider_id,
                AccountModel.account_id,
                AccountModel.account_email,
                AccountModel.created_at,
                AccountModel.updated_at,
            ),
            selectinload(UserModel.roles).load_only(
                RoleModel.id,
                RoleModel.name,
                RoleModel.description,
                RoleModel.created_at,
                RoleModel.updated_at,
            ),
        )

    @classmethod
    def _to_profile(cls, model: UserModel) -> UserProfile:
        return UserProfile(
            user=cls._to_entity(model),
            accounts=tuple(cls._account_profile_to_entity(a) for a in model.accounts),
            roles=tuple(cls._role_to_entity(role) for role in model.roles),
        )

    @staticmethod
    def _account_profile_to_entity(model: AccountModel) -> Account:
        return Account(
            id=UserId(model.id),
            user_id=UserId(model.user_id),
            provider_id=ProviderId(model.provider_id),
            account_id=AccountId(model.account_id),
            account_email=model.account_email,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _role_to_entity(model: RoleModel) -> Role:
        return Role(
            id=RoleId(model.id),
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            name=model.name,
            surname=model.surname,
            email=Email(model.email),
            email_verified=model.email_verified,
            image=model.image,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

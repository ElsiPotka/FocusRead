from __future__ import annotations

from uuid import uuid4

import pytest

from app.application.admin.assign_user_roles import AssignUserRoles
from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import Email, UserId
from app.domain.role.entities import Role
from app.domain.role.value_objects import RoleName
from app.domain.user.entities import User


def _user(user_id: UserId) -> User:
    return User(
        id=user_id,
        name="Admin",
        surname="User",
        email=Email("admin@example.com"),
        email_verified=True,
        is_active=True,
    )


def _roles() -> list[Role]:
    return [
        Role.create(name=RoleName.ADMIN, description="Admin access"),
        Role.create(name=RoleName.MERCHANT, description="Merchant access"),
    ]


class TestAssignUserRoles:
    async def test_assigns_roles_and_returns_current_roles(self, uow):
        user_id = UserId(uuid4())
        roles = _roles()
        uow.users.get.return_value = _user(user_id)
        uow.roles.get_by_names.return_value = roles
        uow.roles.list_for_user.return_value = roles

        result = await AssignUserRoles(uow).execute(
            user_id=user_id.value,
            role_names=[RoleName.ADMIN, RoleName.MERCHANT],
        )

        assert result == roles
        uow.roles.assign_many_to_user.assert_called_once_with(
            user_id,
            [role.id for role in roles],
        )
        uow.commit.assert_called_once()

    async def test_raises_when_user_is_missing(self, uow):
        user_id = uuid4()
        uow.users.get.return_value = None

        with pytest.raises(NotFoundError):
            await AssignUserRoles(uow).execute(
                user_id=user_id,
                role_names=[RoleName.ADMIN],
            )

        uow.roles.get_by_names.assert_not_called()
        uow.commit.assert_not_called()

    async def test_raises_when_a_role_is_missing(self, uow):
        user_id = UserId(uuid4())
        uow.users.get.return_value = _user(user_id)
        uow.roles.get_by_names.return_value = []

        with pytest.raises(NotFoundError):
            await AssignUserRoles(uow).execute(
                user_id=user_id.value,
                role_names=[RoleName.ADMIN],
            )

        uow.roles.assign_many_to_user.assert_not_called()
        uow.commit.assert_not_called()

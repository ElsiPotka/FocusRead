from __future__ import annotations

from uuid import uuid4

from app.application.auth.get_current_user_profile import GetCurrentUserProfile
from app.domain.account.entities import Account
from app.domain.auth.value_objects import Email, HashedPassword, UserId
from app.domain.role.entities import Role
from app.domain.role.value_objects import RoleName
from app.domain.user.entities import User
from app.domain.user.profile import UserProfile


class TestGetCurrentUserProfile:
    async def test_returns_user_and_linked_accounts(self, uow):
        user_id = uuid4()
        user = User(
            id=UserId(user_id),
            name="Jane",
            surname="Doe",
            email=Email("jane@example.com"),
            email_verified=True,
            is_active=True,
        )
        account = Account.create_credential(
            user_id=user.id,
            email=Email("jane@example.com"),
            hashed_password=HashedPassword("$argon2id$hashed"),
        )
        role = Role.create(
            name=RoleName.CLIENT,
            description="Default client access",
        )
        uow.users.get_profile.return_value = UserProfile(
            user=user,
            accounts=(account,),
            roles=(role,),
        )

        use_case = GetCurrentUserProfile(uow)
        result = await use_case.execute(user_id)

        assert result is not None
        assert result.user == user
        assert list(result.accounts) == [account]
        assert list(result.roles) == [role]
        uow.users.get_profile.assert_called_once_with(UserId(user_id))

    async def test_returns_none_when_profile_is_missing(self, uow):
        user_id = uuid4()
        uow.users.get_profile.return_value = None

        use_case = GetCurrentUserProfile(uow)

        assert await use_case.execute(user_id) is None
        uow.users.get_profile.assert_called_once_with(UserId(user_id))

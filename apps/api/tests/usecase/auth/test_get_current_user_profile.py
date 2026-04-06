from __future__ import annotations

from uuid import uuid4

from app.application.auth.get_current_user_profile import GetCurrentUserProfile
from app.domain.account.entities import Account
from app.domain.auth.value_objects import Email, HashedPassword, UserId
from app.domain.user.entities import User


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
        uow.users.get_with_linked_accounts.return_value = (user, [account])

        use_case = GetCurrentUserProfile(uow)
        result = await use_case.execute(user_id)

        assert result is not None
        loaded_user, loaded_accounts = result
        assert loaded_user == user
        assert loaded_accounts == [account]
        uow.users.get_with_linked_accounts.assert_called_once_with(UserId(user_id))

    async def test_returns_none_when_profile_is_missing(self, uow):
        user_id = uuid4()
        uow.users.get_with_linked_accounts.return_value = None

        use_case = GetCurrentUserProfile(uow)

        assert await use_case.execute(user_id) is None
        uow.users.get_with_linked_accounts.assert_called_once_with(UserId(user_id))

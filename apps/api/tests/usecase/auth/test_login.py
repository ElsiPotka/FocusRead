from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.application.auth.login import LoginUser
from app.domain.account.entities import Account
from app.domain.auth.errors import InactiveUserError, InvalidCredentialsError
from app.domain.auth.value_objects import Email, HashedPassword, UserId
from app.domain.user.entities import User


def _active_user() -> User:
    return User.create(name="John", surname="Doe", email=Email("john@example.com"))


def _credential_account(user_id: UserId) -> Account:
    return Account.create_credential(
        user_id=user_id,
        email=Email("john@example.com"),
        hashed_password=HashedPassword("$argon2id$hashed"),
    )


class TestLoginUser:
    async def test_login_succeeds_with_valid_credentials(
        self, uow, jwt_service, session_service
    ):
        user = _active_user()
        uow.users.get_by_email.return_value = user
        uow.accounts.get_credential_by_user.return_value = _credential_account(user.id)

        usecase = LoginUser(uow, jwt_service, session_service)

        with patch(
            "app.application.auth.login.verify_password",
            new_callable=AsyncMock,
            return_value=True,
        ):
            result_user, access_token, refresh_token = await usecase.execute(
                email="john@example.com",
                password="securepassword",
            )

        assert result_user == user
        assert access_token == "access_token_xxx"
        assert refresh_token == "raw_refresh_token_xxx"
        uow.sessions.save.assert_called_once()
        uow.commit.assert_called_once()

    async def test_login_raises_when_user_not_found(
        self, uow, jwt_service, session_service
    ):
        uow.users.get_by_email.return_value = None

        usecase = LoginUser(uow, jwt_service, session_service)

        with (
            patch(
                "app.application.auth.login.dummy_verify",
                new_callable=AsyncMock,
            ),
            pytest.raises(InvalidCredentialsError),
        ):
            await usecase.execute(email="nobody@example.com", password="pass1234")

    async def test_login_raises_when_inactive(
        self, uow, jwt_service, session_service
    ):
        user = _active_user()
        user.deactivate()
        uow.users.get_by_email.return_value = user

        usecase = LoginUser(uow, jwt_service, session_service)

        with pytest.raises(InactiveUserError):
            await usecase.execute(email="john@example.com", password="pass1234")

    async def test_login_raises_when_no_credential_account(
        self, uow, jwt_service, session_service
    ):
        user = _active_user()
        uow.users.get_by_email.return_value = user
        uow.accounts.get_credential_by_user.return_value = None

        usecase = LoginUser(uow, jwt_service, session_service)

        with (
            patch(
                "app.application.auth.login.dummy_verify",
                new_callable=AsyncMock,
            ),
            pytest.raises(InvalidCredentialsError),
        ):
            await usecase.execute(email="john@example.com", password="pass1234")

    async def test_login_raises_when_wrong_password(
        self, uow, jwt_service, session_service
    ):
        user = _active_user()
        uow.users.get_by_email.return_value = user
        uow.accounts.get_credential_by_user.return_value = _credential_account(user.id)

        usecase = LoginUser(uow, jwt_service, session_service)

        with (
            patch(
                "app.application.auth.login.verify_password",
                new_callable=AsyncMock,
                return_value=False,
            ),
            pytest.raises(InvalidCredentialsError),
        ):
            await usecase.execute(email="john@example.com", password="wrongpass")

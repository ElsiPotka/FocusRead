from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.application.auth.register import RegisterUser
from app.domain.auth.errors import EmailAlreadyExistsError
from app.domain.auth.value_objects import Email
from app.domain.role.entities import Role
from app.domain.role.value_objects import RoleName
from app.domain.user.entities import User


class TestRegisterUser:
    async def test_register_creates_user_and_returns_tokens(
        self, uow, jwt_service, session_service
    ):
        client_role = Role.create(
            name=RoleName.CLIENT,
            description="Default client access",
        )
        uow.users.get_by_email.return_value = None
        uow.roles.get_by_name.return_value = client_role

        usecase = RegisterUser(uow, jwt_service, session_service)

        with patch(
            "app.application.auth.register.hash_password",
            new_callable=AsyncMock,
            return_value="$argon2id$hashed",
        ):
            user, access_token, refresh_token = await usecase.execute(
                name="John",
                surname="Doe",
                email="john@example.com",
                password="securepassword",
                user_agent="Mozilla/5.0",
                ip_address="127.0.0.1",
            )

        assert isinstance(user, User)
        assert user.name == "John"
        assert user.email.value == "john@example.com"
        assert access_token == "access_token_xxx"
        assert refresh_token == "raw_refresh_token_xxx"

        uow.users.save.assert_called_once()
        uow.roles.assign_to_user.assert_called_once_with(user.id, client_role.id)
        uow.accounts.save.assert_called_once()
        uow.sessions.save.assert_called_once()
        uow.commit.assert_called_once()
        session_service.cache_session.assert_called_once()
        jwt_service.encode_access_token.assert_called_once_with(
            str(user.id.value),
            "private_pem",
            scopes=["me", "Client"],
        )

    async def test_register_raises_when_email_exists(
        self, uow, jwt_service, session_service
    ):
        existing_user = User.create(
            name="Existing", surname="User", email=Email("john@example.com")
        )
        uow.users.get_by_email.return_value = existing_user

        usecase = RegisterUser(uow, jwt_service, session_service)

        with pytest.raises(EmailAlreadyExistsError):
            await usecase.execute(
                name="John",
                surname="Doe",
                email="john@example.com",
                password="securepassword",
            )

        uow.users.save.assert_not_called()
        uow.roles.assign_to_user.assert_not_called()
        uow.commit.assert_not_called()

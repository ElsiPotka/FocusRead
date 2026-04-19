from __future__ import annotations

from app.application.auth.oauth_callback import (
    HandleOAuthCallback,
    OAuthTokens,
    OAuthUserInfo,
)
from app.domain.account.entities import Account
from app.domain.auth.value_objects import AccountId, Email, ProviderId
from app.domain.role.entities import Role
from app.domain.role.value_objects import RoleName
from app.domain.user.entities import User


def _google_user_info(sub: str = "google-sub-123") -> OAuthUserInfo:
    return {
        "sub": sub,
        "email": "user@gmail.com",
        "given_name": "John",
        "family_name": "Doe",
    }


def _oauth_tokens() -> OAuthTokens:
    return {
        "access_token": "at_xxx",
        "refresh_token": "rt_xxx",
        "id_token": "id_xxx",
        "scope": "openid email",
    }


def _client_role() -> Role:
    return Role.create(
        name=RoleName.CLIENT,
        description="Default client access",
    )


class TestHandleOAuthCallbackExistingAccount:
    async def test_updates_tokens_for_existing_account(
        self, uow, jwt_service, session_service
    ):
        user = User.create(name="John", surname="Doe", email=Email("user@gmail.com"))
        existing_account = Account.create_oauth(
            user_id=user.id,
            provider_id=ProviderId("google"),
            account_id=AccountId("google-sub-123"),
            access_token="old_at",
        )
        uow.roles.list_for_user.return_value = [_client_role()]
        uow.accounts.get_by_provider.return_value = existing_account
        uow.users.get.return_value = user

        usecase = HandleOAuthCallback(uow, jwt_service, session_service)
        result_user, access_token, refresh_token = await usecase.execute(
            provider="google",
            oauth_user_info=_google_user_info(),
            oauth_tokens=_oauth_tokens(),
        )

        assert result_user == user
        assert access_token == "access_token_xxx"
        assert existing_account.access_token == "at_xxx"
        uow.accounts.save.assert_called_once()
        uow.sessions.save.assert_called_once()
        uow.commit.assert_called_once()
        jwt_service.encode_access_token.assert_called_once_with(
            str(user.id.value),
            "private_pem",
            scopes=["me", "Client"],
        )


class TestHandleOAuthCallbackNewUserNoEmail:
    async def test_creates_new_user_when_no_matching_email(
        self, uow, jwt_service, session_service
    ):
        client_role = _client_role()
        uow.accounts.get_by_provider.return_value = None
        uow.users.get_by_email.return_value = None
        uow.roles.get_by_name.return_value = client_role

        usecase = HandleOAuthCallback(uow, jwt_service, session_service)
        user, access_token, refresh_token = await usecase.execute(
            provider="google",
            oauth_user_info=_google_user_info(),
            oauth_tokens=_oauth_tokens(),
        )

        assert user.name == "John"
        assert user.email_verified is True
        uow.users.save.assert_called_once()
        uow.roles.assign_to_user.assert_called_once_with(user.id, client_role.id)
        uow.accounts.save.assert_called_once()
        uow.sessions.save.assert_called_once()
        jwt_service.encode_access_token.assert_called_once_with(
            str(user.id.value),
            "private_pem",
            scopes=["me", "Client"],
        )


class TestHandleOAuthCallbackLinkExistingUser:
    async def test_links_account_to_existing_user_with_same_email(
        self, uow, jwt_service, session_service
    ):
        existing_user = User.create(
            name="Jane", surname="Doe", email=Email("user@gmail.com")
        )
        uow.accounts.get_by_provider.return_value = None
        uow.users.get_by_email.return_value = existing_user
        uow.roles.list_for_user.return_value = [_client_role()]

        usecase = HandleOAuthCallback(uow, jwt_service, session_service)
        user, access_token, refresh_token = await usecase.execute(
            provider="google",
            oauth_user_info=_google_user_info(),
            oauth_tokens=_oauth_tokens(),
        )

        assert user == existing_user
        uow.users.save.assert_not_called()
        uow.roles.assign_to_user.assert_not_called()
        uow.accounts.save.assert_called_once()

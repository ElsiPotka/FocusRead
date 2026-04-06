from __future__ import annotations

from app.application.auth.oauth_callback import HandleOAuthCallback
from app.domain.account.entities import Account
from app.domain.auth.value_objects import AccountId, Email, ProviderId, UserId
from app.domain.user.entities import User


def _google_user_info(sub: str = "google-sub-123") -> dict:
    return {
        "sub": sub,
        "email": "user@gmail.com",
        "given_name": "John",
        "family_name": "Doe",
    }


def _oauth_tokens() -> dict:
    return {
        "access_token": "at_xxx",
        "refresh_token": "rt_xxx",
        "id_token": "id_xxx",
        "scope": "openid email",
    }


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


class TestHandleOAuthCallbackNewUserNoEmail:
    async def test_creates_new_user_when_no_matching_email(
        self, uow, jwt_service, session_service
    ):
        uow.accounts.get_by_provider.return_value = None
        uow.users.get_by_email.return_value = None

        usecase = HandleOAuthCallback(uow, jwt_service, session_service)
        user, access_token, refresh_token = await usecase.execute(
            provider="google",
            oauth_user_info=_google_user_info(),
            oauth_tokens=_oauth_tokens(),
        )

        assert user.name == "John"
        assert user.email_verified is True
        uow.users.save.assert_called_once()
        uow.accounts.save.assert_called_once()
        uow.sessions.save.assert_called_once()


class TestHandleOAuthCallbackLinkExistingUser:
    async def test_links_account_to_existing_user_with_same_email(
        self, uow, jwt_service, session_service
    ):
        existing_user = User.create(
            name="Jane", surname="Doe", email=Email("user@gmail.com")
        )
        uow.accounts.get_by_provider.return_value = None
        uow.users.get_by_email.return_value = existing_user

        usecase = HandleOAuthCallback(uow, jwt_service, session_service)
        user, access_token, refresh_token = await usecase.execute(
            provider="google",
            oauth_user_info=_google_user_info(),
            oauth_tokens=_oauth_tokens(),
        )

        assert user == existing_user
        uow.users.save.assert_not_called()
        uow.accounts.save.assert_called_once()

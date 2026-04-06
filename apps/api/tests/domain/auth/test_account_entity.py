from __future__ import annotations

from app.domain.account.entities import Account
from app.domain.auth.value_objects import (
    AccountId,
    Email,
    HashedPassword,
    ProviderId,
    UserId,
)


class TestAccountCreateCredential:
    def test_creates_with_credential_provider(self):
        user_id = UserId.generate()
        email = Email("test@example.com")
        hashed = HashedPassword("$argon2id$hash")

        account = Account.create_credential(
            user_id=user_id, email=email, hashed_password=hashed
        )

        assert account.provider_id == ProviderId("credential")
        assert account.account_id == AccountId(email.value)
        assert account.account_email == email.value
        assert account.hashed_password == hashed
        assert account.user_id == user_id

    def test_oauth_fields_are_none(self):
        account = Account.create_credential(
            user_id=UserId.generate(),
            email=Email("a@b.com"),
            hashed_password=HashedPassword("hash"),
        )
        assert account.access_token is None
        assert account.refresh_token is None
        assert account.id_token is None
        assert account.scope is None


class TestAccountCreateOAuth:
    def test_creates_with_provider(self):
        user_id = UserId.generate()
        account = Account.create_oauth(
            user_id=user_id,
            provider_id=ProviderId("google"),
            account_id=AccountId("google-sub-123"),
            account_email="user@gmail.com",
            access_token="at_xxx",
            refresh_token="rt_xxx",
            scope="openid email profile",
        )

        assert account.provider_id == ProviderId("google")
        assert account.account_id == AccountId("google-sub-123")
        assert account.account_email == "user@gmail.com"
        assert account.access_token == "at_xxx"
        assert account.hashed_password is None

    def test_password_is_none_for_oauth(self):
        account = Account.create_oauth(
            user_id=UserId.generate(),
            provider_id=ProviderId("apple"),
            account_id=AccountId("apple-sub-456"),
        )
        assert account.hashed_password is None


class TestAccountUpdateOAuthTokens:
    def test_updates_tokens(self):
        account = Account.create_oauth(
            user_id=UserId.generate(),
            provider_id=ProviderId("google"),
            account_id=AccountId("sub-123"),
            access_token="old_at",
        )
        original_updated = account.updated_at

        account.update_oauth_tokens(
            access_token="new_at",
            refresh_token="new_rt",
            id_token="new_id",
            scope="openid",
        )

        assert account.access_token == "new_at"
        assert account.refresh_token == "new_rt"
        assert account.id_token == "new_id"
        assert account.scope == "openid"
        assert account.updated_at >= original_updated

    def test_clears_tokens_when_none(self):
        account = Account.create_oauth(
            user_id=UserId.generate(),
            provider_id=ProviderId("google"),
            account_id=AccountId("sub-123"),
            access_token="old",
        )

        account.update_oauth_tokens()

        assert account.access_token is None
        assert account.refresh_token is None


class TestAccountEquality:
    def test_same_id_equal(self):
        uid = UserId.generate()
        a1 = Account(
            id=uid,
            user_id=UserId.generate(),
            provider_id=ProviderId("credential"),
            account_id=AccountId("a@b.com"),
        )
        a2 = Account(
            id=uid,
            user_id=UserId.generate(),
            provider_id=ProviderId("google"),
            account_id=AccountId("different"),
        )
        assert a1 == a2

    def test_different_id_not_equal(self):
        a1 = Account.create_credential(
            user_id=UserId.generate(),
            email=Email("a@b.com"),
            hashed_password=HashedPassword("h"),
        )
        a2 = Account.create_credential(
            user_id=UserId.generate(),
            email=Email("a@b.com"),
            hashed_password=HashedPassword("h"),
        )
        assert a1 != a2

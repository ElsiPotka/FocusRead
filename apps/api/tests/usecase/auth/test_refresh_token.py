from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.application.auth.refresh_token import RefreshAccessToken
from app.domain.auth.errors import (
    InactiveUserError,
    InvalidRefreshTokenError,
    SessionExpiredError,
)
from app.domain.auth.value_objects import Email, RefreshTokenHash, UserId
from app.domain.session.entities import Session
from app.domain.user.entities import User


def _user() -> User:
    return User.create(name="A", surname="B", email=Email("a@b.com"))


def _session(user_id: UserId, *, expired: bool = False) -> Session:
    delta = timedelta(days=-1) if expired else timedelta(days=7)
    return Session.create(
        user_id=user_id,
        token_hash=RefreshTokenHash("a" * 64),
        expires_at=datetime.now(UTC) + delta,
    )


class TestRefreshAccessToken:
    async def test_refresh_rotates_session_and_returns_new_tokens(
        self, uow, jwt_service, session_service
    ):
        user = _user()
        session = _session(user.id)
        uow.sessions.get_by_token_hash.return_value = session
        uow.users.get.return_value = user

        usecase = RefreshAccessToken(uow, jwt_service, session_service)
        result_user, access_token, refresh_token = await usecase.execute(
            raw_refresh_token="raw_token",
        )

        assert result_user == user
        assert access_token == "access_token_xxx"
        assert refresh_token == "raw_refresh_token_xxx"
        uow.sessions.save.assert_called_once()
        uow.commit.assert_called_once()
        session_service.invalidate_cached_session.assert_called()
        session_service.cache_session.assert_called_once()

    async def test_refresh_raises_when_session_not_found(
        self, uow, jwt_service, session_service
    ):
        uow.sessions.get_by_token_hash.return_value = None

        usecase = RefreshAccessToken(uow, jwt_service, session_service)

        with pytest.raises(InvalidRefreshTokenError):
            await usecase.execute(raw_refresh_token="bad_token")

    async def test_refresh_raises_and_deletes_when_expired(
        self, uow, jwt_service, session_service
    ):
        user = _user()
        expired_session = _session(user.id, expired=True)
        uow.sessions.get_by_token_hash.return_value = expired_session

        usecase = RefreshAccessToken(uow, jwt_service, session_service)

        with pytest.raises(SessionExpiredError):
            await usecase.execute(raw_refresh_token="expired_token")

        uow.sessions.delete.assert_called_once_with(expired_session.id)
        uow.commit.assert_called_once()

    async def test_refresh_raises_when_user_not_found(
        self, uow, jwt_service, session_service
    ):
        session = _session(UserId.generate())
        uow.sessions.get_by_token_hash.return_value = session
        uow.users.get.return_value = None

        usecase = RefreshAccessToken(uow, jwt_service, session_service)

        with pytest.raises(InvalidRefreshTokenError):
            await usecase.execute(raw_refresh_token="raw_token")

    async def test_refresh_raises_when_user_inactive(
        self, uow, jwt_service, session_service
    ):
        user = _user()
        user.deactivate()
        session = _session(user.id)
        uow.sessions.get_by_token_hash.return_value = session
        uow.users.get.return_value = user

        usecase = RefreshAccessToken(uow, jwt_service, session_service)

        with pytest.raises(InactiveUserError):
            await usecase.execute(raw_refresh_token="raw_token")

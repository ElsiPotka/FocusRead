from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.admin.get_user_books import GetUserBooks
from app.application.admin.get_user_detail import GetUserDetail
from app.application.admin.impersonate_user import ImpersonateUser
from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import Email, UserId
from app.domain.user.entities import User
from app.domain.user.profile import UserProfile


def _make_user(*, user_id=None, email="test@example.com"):
    return User(
        id=UserId(user_id or uuid4()),
        name="Test",
        surname="User",
        email=Email(email),
    )


# --- GetUserDetail ---


class TestGetUserDetail:
    @pytest.mark.anyio
    async def test_returns_profile(self, uow, user_repo):
        uid = uuid4()
        user = _make_user(user_id=uid)
        profile = UserProfile(user=user, accounts=(), roles=())
        user_repo.get_profile.return_value = profile

        result = await GetUserDetail(uow).execute(user_id=uid)

        assert result.user.id.value == uid
        user_repo.get_profile.assert_awaited_once()

    @pytest.mark.anyio
    async def test_raises_not_found(self, uow, user_repo):
        user_repo.get_profile.return_value = None

        with pytest.raises(NotFoundError, match="User not found"):
            await GetUserDetail(uow).execute(user_id=uuid4())


# --- GetUserBooks ---


class TestGetUserBooks:
    @pytest.mark.anyio
    async def test_delegates_to_repo(self, uow, book_repo):
        uid = uuid4()
        book_repo.list_for_owner.return_value = []

        result = await GetUserBooks(uow).execute(user_id=uid)

        assert result == []
        book_repo.list_for_owner.assert_awaited_once()


# --- ImpersonateUser ---


class TestImpersonateUser:
    @pytest.mark.anyio
    async def test_by_user_id(self, uow, user_repo, role_repo, session_repo):
        uid = uuid4()
        user = _make_user(user_id=uid)
        user_repo.get.return_value = user
        role_repo.list_for_user.return_value = []

        jwt_service = MagicMock()
        jwt_service.get_or_create_key_pair = AsyncMock(return_value=("priv", "pub"))
        jwt_service.encode_access_token.return_value = "access_tok"

        session_service = MagicMock()
        session_service.generate_refresh_token.return_value = "raw_refresh"
        session_service.hash_token.return_value = "a" * 64
        session_service.cache_session = AsyncMock()

        use_case = ImpersonateUser(uow, jwt_service, session_service)
        result_user, access, refresh = await use_case.execute(user_id=uid)

        assert result_user.id.value == uid
        assert access == "access_tok"
        assert refresh == "raw_refresh"
        session_repo.save.assert_awaited_once()
        uow.commit.assert_awaited_once()

    @pytest.mark.anyio
    async def test_by_email(self, uow, user_repo, role_repo, session_repo):
        user = _make_user(email="admin@test.com")
        user_repo.get_by_email.return_value = user
        role_repo.list_for_user.return_value = []

        jwt_service = MagicMock()
        jwt_service.get_or_create_key_pair = AsyncMock(return_value=("priv", "pub"))
        jwt_service.encode_access_token.return_value = "tok"

        session_service = MagicMock()
        session_service.generate_refresh_token.return_value = "ref"
        session_service.hash_token.return_value = "b" * 64
        session_service.cache_session = AsyncMock()

        use_case = ImpersonateUser(uow, jwt_service, session_service)
        result_user, _, _ = await use_case.execute(email="admin@test.com")

        assert result_user.email.value == "admin@test.com"

    @pytest.mark.anyio
    async def test_raises_when_no_identifier(self, uow):
        jwt_service = AsyncMock()
        session_service = MagicMock()

        with pytest.raises(NotFoundError, match="Provide either"):
            await ImpersonateUser(uow, jwt_service, session_service).execute()

    @pytest.mark.anyio
    async def test_raises_when_user_not_found(self, uow, user_repo):
        user_repo.get.return_value = None

        jwt_service = AsyncMock()
        session_service = MagicMock()

        with pytest.raises(NotFoundError, match="User not found"):
            await ImpersonateUser(uow, jwt_service, session_service).execute(
                user_id=uuid4()
            )

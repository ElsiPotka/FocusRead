from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.application.auth.logout import LogoutUser
from app.domain.auth.errors import InvalidRefreshTokenError
from app.domain.auth.value_objects import RefreshTokenHash, UserId
from app.domain.session.entities import Session


class TestLogoutUser:
    async def test_logout_deletes_session_and_invalidates_cache(
        self, uow, session_service
    ):
        user_id = UserId.generate()
        session = Session.create(
            user_id=user_id,
            token_hash=RefreshTokenHash("a" * 64),
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        uow.sessions.get_by_token_hash.return_value = session

        usecase = LogoutUser(uow, session_service)
        await usecase.execute(raw_refresh_token="raw_token")

        uow.sessions.delete.assert_called_once_with(session.id)
        uow.commit.assert_called_once()
        session_service.invalidate_cached_session.assert_called_once()
        session_service.invalidate_current_user.assert_called_once_with(
            str(user_id.value)
        )

    async def test_logout_raises_when_session_not_found(self, uow, session_service):
        uow.sessions.get_by_token_hash.return_value = None

        usecase = LogoutUser(uow, session_service)

        with pytest.raises(InvalidRefreshTokenError):
            await usecase.execute(raw_refresh_token="bad_token")

        uow.sessions.delete.assert_not_called()

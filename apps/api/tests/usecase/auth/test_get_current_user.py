from __future__ import annotations

from uuid import uuid4

from app.application.auth.get_current_user import GetCurrentUser
from app.domain.auth.value_objects import Email, UserId
from app.domain.user.entities import User


class TestGetCurrentUser:
    async def test_returns_user_from_cache(self, uow, session_service):
        user_id = uuid4()
        session_service.get_cached_current_user.return_value = {
            "name": "John",
            "surname": "Doe",
            "email": "john@example.com",
            "email_verified": True,
            "image": None,
            "is_active": True,
        }

        usecase = GetCurrentUser(uow, session_service)
        user = await usecase.execute(user_id)

        assert user is not None
        assert user.name == "John"
        assert user.email.value == "john@example.com"
        uow.users.get.assert_not_called()

    async def test_fetches_from_db_when_not_cached(self, uow, session_service):
        user_id = uuid4()
        session_service.get_cached_current_user.return_value = None

        db_user = User(
            id=UserId(user_id),
            name="Jane",
            surname="Doe",
            email=Email("jane@example.com"),
            email_verified=False,
            is_active=True,
        )
        uow.users.get.return_value = db_user

        usecase = GetCurrentUser(uow, session_service)
        user = await usecase.execute(user_id)

        assert user is not None
        assert user.name == "Jane"
        uow.users.get.assert_called_once()
        session_service.cache_current_user.assert_called_once()

    async def test_returns_none_when_user_not_found(self, uow, session_service):
        session_service.get_cached_current_user.return_value = None
        uow.users.get.return_value = None

        usecase = GetCurrentUser(uow, session_service)
        user = await usecase.execute(uuid4())

        assert user is None
        session_service.cache_current_user.assert_not_called()

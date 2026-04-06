from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.auth.entities import User
from app.domain.auth.value_objects import Email, UserId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.auth.session_service import SessionService


class GetCurrentUser:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        session_service: SessionService,
    ) -> None:
        self._uow = uow
        self._session_svc = session_service

    async def execute(self, user_id: UUID) -> User | None:
        cached = await self._session_svc.get_cached_current_user(str(user_id))
        if cached is not None:
            return User(
                id=UserId(user_id),
                name=cached["name"],
                surname=cached["surname"],
                email=Email(cached["email"]),
                email_verified=cached["email_verified"],
                image=cached.get("image"),
                is_active=cached["is_active"],
            )

        user = await self._uow.users.get(UserId(user_id))
        if user is None:
            return None

        await self._session_svc.cache_current_user(
            str(user_id),
            {
                "name": user.name,
                "surname": user.surname,
                "email": user.email.value,
                "email_verified": user.email_verified,
                "image": user.image,
                "is_active": user.is_active,
            },
        )

        return user

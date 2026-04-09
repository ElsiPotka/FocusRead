from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId
    from app.domain.user_book_state.entities import UserBookState


class UserBookStateRepository(ABC):
    @abstractmethod
    async def save(self, state: UserBookState) -> None: ...

    @abstractmethod
    async def get(
        self, *, user_id: UserId, book_id: BookId
    ) -> UserBookState | None: ...

    @abstractmethod
    async def list_favorites(self, *, user_id: UserId) -> list[UserBookState]: ...

    @abstractmethod
    async def list_archived(self, *, user_id: UserId) -> list[UserBookState]: ...

    @abstractmethod
    async def list_completed(self, *, user_id: UserId) -> list[UserBookState]: ...

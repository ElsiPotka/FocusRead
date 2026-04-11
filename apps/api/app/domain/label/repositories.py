from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.auth.value_objects import UserId
    from app.domain.books.value_objects import BookId
    from app.domain.label.entities import Label
    from app.domain.label.value_objects import LabelId, LabelSlug


class LabelRepository(ABC):
    @abstractmethod
    async def save(self, label: Label) -> None: ...

    @abstractmethod
    async def get(self, label_id: LabelId) -> Label | None: ...

    @abstractmethod
    async def get_for_owner(
        self, *, label_id: LabelId, user_id: UserId
    ) -> Label | None: ...

    @abstractmethod
    async def get_by_slug(
        self, *, slug: LabelSlug, user_id: UserId
    ) -> Label | None: ...

    @abstractmethod
    async def list_for_user(self, *, user_id: UserId) -> list[Label]: ...

    @abstractmethod
    async def get_system(self, *, label_id: LabelId) -> Label | None: ...

    @abstractmethod
    async def list_system(self) -> list[Label]: ...

    @abstractmethod
    async def delete(self, label_id: LabelId) -> None: ...

    @abstractmethod
    async def assign_to_book(
        self, *, label_id: LabelId, book_id: BookId
    ) -> None: ...

    @abstractmethod
    async def unassign_from_book(
        self, *, label_id: LabelId, book_id: BookId
    ) -> None: ...

    @abstractmethod
    async def list_for_book(self, *, book_id: BookId) -> list[Label]: ...

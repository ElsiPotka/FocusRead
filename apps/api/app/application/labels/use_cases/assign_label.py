from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.value_objects import BookId
from app.domain.label.value_objects import LabelId

if TYPE_CHECKING:
    from uuid import UUID

    from app.application.common.unit_of_work import AbstractUnitOfWork


class AssignLabel:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        *,
        book_id: UUID,
        label_id: UUID,
        user_id: UUID,
    ) -> None:
        book = await self._uow.books.get_for_owner(
            book_id=BookId(book_id),
            owner_user_id=UserId(user_id),
        )
        if book is None:
            raise NotFoundError("Book not found")

        label = await self._uow.labels.get_for_owner(
            label_id=LabelId(label_id),
            user_id=UserId(user_id),
        )
        if label is None:
            raise NotFoundError("Label not found")
        library_item = await self._uow.library_items.get_active_for_user_book(
            user_id=UserId(user_id),
            book_id=book.id,
        )
        if library_item is None:
            raise NotFoundError("Library item not found")

        await self._uow.labels.assign_to_library_item(
            label_id=label.id,
            library_item_id=library_item.id,
        )
        await self._uow.commit()

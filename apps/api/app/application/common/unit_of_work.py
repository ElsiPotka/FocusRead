from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

from app.config.logger import log

if TYPE_CHECKING:
    from app.domain.books.repositories import BookRepository


class AbstractUnitOfWork(ABC):
    books: BookRepository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            log.opt(exception=(exc_type, exc_val, exc_tb)).warning(
                "Rolling back transaction due to an exception.",
            )
            await self.rollback()

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

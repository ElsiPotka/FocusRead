from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.config.db import get_db
from app.infrastructure.persistence.repositories.book_repository import (
    SqlAlchemyBookRepository,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.books = SqlAlchemyBookRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


async def get_uow(
    session: AsyncSession = Depends(get_db),
) -> AsyncIterator[SqlAlchemyUnitOfWork]:
    yield SqlAlchemyUnitOfWork(session)

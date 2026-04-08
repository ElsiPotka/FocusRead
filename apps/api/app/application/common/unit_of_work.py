from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

from app.infrastructure.logging.logger import log

if TYPE_CHECKING:
    from app.domain.auth.repositories import (
        AccountRepository,
        JWTSigningKeyRepository,
        SessionRepository,
        UserRepository,
    )
    from app.domain.book_chunks.repositories import BookChunkRepository
    from app.domain.books.repositories import BookRepository
    from app.domain.role.repositories import RoleRepository


class AbstractUnitOfWork(ABC):
    books: BookRepository
    book_chunks: BookChunkRepository
    users: UserRepository
    roles: RoleRepository
    accounts: AccountRepository
    sessions: SessionRepository
    jwt_signing_keys: JWTSigningKeyRepository

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

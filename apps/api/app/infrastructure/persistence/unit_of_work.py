from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from app.application.common.unit_of_work import AbstractUnitOfWork
from app.infrastructure.persistence.db import get_db
from app.infrastructure.persistence.repositories.account_repository import (
    SqlAlchemyAccountRepository,
)
from app.infrastructure.persistence.repositories.book_chunk_repository import (
    SqlAlchemyBookChunkRepository,
)
from app.infrastructure.persistence.repositories.book_repository import (
    SqlAlchemyBookRepository,
)
from app.infrastructure.persistence.repositories.book_toc_entry_repository import (
    SqlAlchemyBookTOCEntryRepository,
)
from app.infrastructure.persistence.repositories.bookmark_repository import (
    SqlAlchemyBookmarkRepository,
)
from app.infrastructure.persistence.repositories.contributor_repository import (
    SqlAlchemyContributorRepository,
)
from app.infrastructure.persistence.repositories.jwt_signing_key_repository import (
    SqlAlchemyJWTSigningKeyRepository,
)
from app.infrastructure.persistence.repositories.label_repository import (
    SqlAlchemyLabelRepository,
)
from app.infrastructure.persistence.repositories.reading_session_repository import (
    SqlAlchemyReadingSessionRepository,
)
from app.infrastructure.persistence.repositories.reading_stat_repository import (
    SqlAlchemyReadingStatRepository,
)
from app.infrastructure.persistence.repositories.role_repository import (
    SqlAlchemyRoleRepository,
)
from app.infrastructure.persistence.repositories.session_repository import (
    SqlAlchemySessionRepository,
)
from app.infrastructure.persistence.repositories.shelf_repository import (
    SqlAlchemyShelfRepository,
)
from app.infrastructure.persistence.repositories.theme_repository import (
    SqlAlchemyThemeRepository,
)
from app.infrastructure.persistence.repositories.user_book_state_repository import (
    SqlAlchemyUserBookStateRepository,
)
from app.infrastructure.persistence.repositories.user_repository import (
    SqlAlchemyUserRepository,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.books = SqlAlchemyBookRepository(session)
        self.book_chunks = SqlAlchemyBookChunkRepository(session)
        self.book_toc_entries = SqlAlchemyBookTOCEntryRepository(session)
        self.bookmarks = SqlAlchemyBookmarkRepository(session)
        self.contributors = SqlAlchemyContributorRepository(session)
        self.labels = SqlAlchemyLabelRepository(session)
        self.reading_sessions = SqlAlchemyReadingSessionRepository(session)
        self.reading_stats = SqlAlchemyReadingStatRepository(session)
        self.shelves = SqlAlchemyShelfRepository(session)
        self.themes = SqlAlchemyThemeRepository(session)
        self.user_book_states = SqlAlchemyUserBookStateRepository(session)
        self.users = SqlAlchemyUserRepository(session)
        self.roles = SqlAlchemyRoleRepository(session)
        self.accounts = SqlAlchemyAccountRepository(session)
        self.sessions = SqlAlchemySessionRepository(session)
        self.jwt_signing_keys = SqlAlchemyJWTSigningKeyRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


async def get_uow(
    session: AsyncSession = Depends(get_db),
) -> AsyncIterator[SqlAlchemyUnitOfWork]:
    yield SqlAlchemyUnitOfWork(session)

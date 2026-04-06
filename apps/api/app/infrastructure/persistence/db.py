from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.config.settings import settings
from app.infrastructure.logging.logger import log

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from sqlalchemy.ext.asyncio import AsyncEngine


class DatabaseSessionManager:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def init(self, database_url: str) -> None:
        if self._engine is not None and self._sessionmaker is not None:
            return

        self._engine = create_async_engine(
            database_url,
            echo=settings.DB_ECHO,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def close(self) -> None:
        if self._engine is None:
            return

        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise RuntimeError("DatabaseSessionManager is not initialized.")

        async with self._engine.begin() as connection:
            yield connection

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise RuntimeError("DatabaseSessionManager is not initialized.")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @property
    def is_initialized(self) -> bool:
        return self._engine is not None and self._sessionmaker is not None


sessionmanager = DatabaseSessionManager()


async def init_db(*, check_connection: bool) -> None:
    sessionmanager.init(settings.SQLALCHEMY_DATABASE_URI)

    if not check_connection:
        log.info("Database engine initialized without eager connection check.")
        return

    async with sessionmanager.connect() as connection:
        await connection.execute(text("SELECT 1"))

    log.info("Database initialized and connection verified.")


async def close_db() -> None:
    await sessionmanager.close()
    log.info("Database engine disposed.")


async def get_db() -> AsyncIterator[AsyncSession]:
    if not sessionmanager.is_initialized:
        await init_db(check_connection=False)

    async with sessionmanager.session() as session:
        yield session


@contextlib.asynccontextmanager
async def get_db_context() -> AsyncIterator[AsyncSession]:
    if not sessionmanager.is_initialized:
        await init_db(check_connection=False)

    async with sessionmanager.session() as session:
        yield session

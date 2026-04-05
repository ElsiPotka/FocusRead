from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import select

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Mapped


class SoftDeleteQueryMixin:
    if TYPE_CHECKING:
        id: Mapped[UUID]
        deleted_at: Mapped[datetime | None]

        @property
        def is_deleted(self) -> bool: ...

        def restore(self) -> None: ...

    @classmethod
    async def all(cls, session: AsyncSession):
        result = await session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    async def with_trashed(cls, session: AsyncSession):
        result = await session.execute(
            select(cls),
            execution_options={"include_deleted": True},
        )
        return result.scalars().all()

    @classmethod
    async def only_trashed(cls, session: AsyncSession):
        result = await session.execute(
            select(cls).where(cls.deleted_at.is_not(None)),
            execution_options={"include_deleted": True},
        )
        return result.scalars().all()

    @classmethod
    async def find_with_trashed(cls, session: AsyncSession, id: Any):
        result = await session.execute(
            select(cls).where(cls.id == id),
            execution_options={"include_deleted": True},
        )
        return result.scalars().one_or_none()

    @classmethod
    async def restore_by_id(cls, session: AsyncSession, id: Any):
        record = await cls.find_with_trashed(session, id)
        if record and record.is_deleted:
            record.restore()
            await session.flush()
            return record
        return None

    @classmethod
    async def force_delete(cls, session: AsyncSession, id: Any):
        record = await cls.find_with_trashed(session, id)
        if record:
            await session.delete(record)
            await session.flush()
            return True
        return False

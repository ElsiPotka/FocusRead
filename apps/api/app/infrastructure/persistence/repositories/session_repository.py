from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from app.domain.auth.entities import Session
from app.domain.auth.repositories import SessionRepository
from app.domain.auth.value_objects import RefreshTokenHash, UserId
from app.infrastructure.persistence.models.session import SessionModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession as DbSession


class SqlAlchemySessionRepository(SessionRepository):
    def __init__(self, session: DbSession) -> None:
        self.session = session

    async def save(self, session: Session) -> None:
        model = await self.session.get(SessionModel, session.id.value)

        if model is None:
            model = SessionModel(
                id=session.id.value,
                user_id=session.user_id.value,
                token_hash=session.token_hash.value,
                expires_at=session.expires_at,
                user_agent=session.user_agent,
                ip_address=session.ip_address,
            )
            self.session.add(model)
            return

        model.token_hash = session.token_hash.value
        model.expires_at = session.expires_at
        model.user_agent = session.user_agent
        model.ip_address = session.ip_address

    async def get_by_token_hash(self, token_hash: RefreshTokenHash) -> Session | None:
        stmt = select(SessionModel).where(SessionModel.token_hash == token_hash.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def delete(self, session_id: UserId) -> None:
        stmt = delete(SessionModel).where(SessionModel.id == session_id.value)
        await self.session.execute(stmt)

    async def delete_all_for_user(self, user_id: UserId) -> None:
        stmt = delete(SessionModel).where(SessionModel.user_id == user_id.value)
        await self.session.execute(stmt)

    @staticmethod
    def _to_entity(model: SessionModel) -> Session:
        return Session(
            id=UserId(model.id),
            user_id=UserId(model.user_id),
            token_hash=RefreshTokenHash(model.token_hash),
            expires_at=model.expires_at,
            user_agent=model.user_agent,
            ip_address=model.ip_address,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

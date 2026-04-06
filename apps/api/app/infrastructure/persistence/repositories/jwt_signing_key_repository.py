from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.auth.repositories import JWTSigningKeyRepository
from app.infrastructure.persistence.models.jwt_signing_key import JWTSigningKeyModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyJWTSigningKeyRepository(JWTSigningKeyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_key_pair(
        self,
        *,
        public_key: str,
        private_key: str,
        algorithm: str,
    ) -> None:
        model = JWTSigningKeyModel(
            public_key=public_key,
            private_key=private_key,
            algorithm=algorithm,
        )
        self.session.add(model)

    async def get_active_key_pair(self) -> tuple[str, str] | None:
        stmt = select(JWTSigningKeyModel).where(JWTSigningKeyModel.expires_at.is_(None))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return (model.private_key, model.public_key)

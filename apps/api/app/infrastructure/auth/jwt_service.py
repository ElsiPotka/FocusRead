from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.infrastructure.cache.keys import build_cache_key
from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.cache.redis_cache import RedisCache

_ALGORITHM = "RS256"
_KEY_PAIR_CACHE_KEY = build_cache_key("auth", "jwt", "active_key_pair")


class JWTService:
    def __init__(self, cache: RedisCache) -> None:
        self._cache = cache

    async def get_or_create_key_pair(self, uow: AbstractUnitOfWork) -> tuple[str, str]:
        cached = await self._cache.get_json(_KEY_PAIR_CACHE_KEY)
        if cached is not None:
            return (cached["private_key"], cached["public_key"])

        key_pair = await uow.jwt_signing_keys.get_active_key_pair()
        if key_pair is not None:
            private_pem, public_pem = key_pair
            await self._cache.set_json(
                _KEY_PAIR_CACHE_KEY,
                {"private_key": private_pem, "public_key": public_pem},
                ttl_seconds=settings.JWT_KEY_PAIR_CACHE_TTL_SECONDS,
            )
            return (private_pem, public_pem)

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")
        public_pem = (
            private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("utf-8")
        )

        await uow.jwt_signing_keys.save_key_pair(
            public_key=public_pem,
            private_key=private_pem,
            algorithm=_ALGORITHM,
        )
        await uow.commit()

        await self._cache.set_json(
            _KEY_PAIR_CACHE_KEY,
            {"private_key": private_pem, "public_key": public_pem},
            ttl_seconds=settings.JWT_KEY_PAIR_CACHE_TTL_SECONDS,
        )

        return (private_pem, public_pem)

    def encode_access_token(self, user_id: str, private_key: str) -> str:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, private_key, algorithm=_ALGORITHM)

    def decode_access_token(self, token: str, public_key: str) -> dict[str, Any]:
        return jwt.decode(token, public_key, algorithms=[_ALGORITHM])

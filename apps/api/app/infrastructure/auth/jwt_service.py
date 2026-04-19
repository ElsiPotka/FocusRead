from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, TypedDict, TypeGuard, cast

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.infrastructure.cache.keys import build_cache_key
from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from app.application.common.unit_of_work import AbstractUnitOfWork
    from app.infrastructure.cache.redis_cache import RedisCache
    from app.types import JSONValue

_ALGORITHM = "RS256"
_KEY_PAIR_CACHE_KEY = build_cache_key("auth", "jwt", "active_key_pair")


class KeyPairCacheEntry(TypedDict):
    private_key: str
    public_key: str


class DecodedAccessTokenPayload(TypedDict):
    sub: str
    scope: str
    iat: int
    exp: int


def _is_key_pair_cache_entry(value: JSONValue) -> TypeGuard[KeyPairCacheEntry]:
    return (
        isinstance(value, dict)
        and isinstance(value.get("private_key"), str)
        and isinstance(value.get("public_key"), str)
    )


def _is_decoded_access_token_payload(
    value: object,
) -> TypeGuard[DecodedAccessTokenPayload]:
    if not isinstance(value, dict):
        return False
    payload = cast("dict[str, object]", value)
    return (
        isinstance(payload.get("sub"), str)
        and isinstance(payload.get("scope"), str)
        and isinstance(payload.get("iat"), int)
        and isinstance(payload.get("exp"), int)
    )


class JWTService:
    def __init__(self, cache: RedisCache) -> None:
        self._cache = cache

    async def get_or_create_key_pair(self, uow: AbstractUnitOfWork) -> tuple[str, str]:
        cached = await self._cache.get_json(_KEY_PAIR_CACHE_KEY)
        if cached is not None and _is_key_pair_cache_entry(cached):
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

    def encode_access_token(
        self,
        user_id: str,
        private_key: str,
        *,
        scopes: list[str] | None = None,
    ) -> str:
        now = datetime.now(UTC)
        payload: dict[str, str | datetime] = {
            "sub": user_id,
            "scope": " ".join(scopes or []),
            "iat": now,
            "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, private_key, algorithm=_ALGORITHM)

    def decode_access_token(
        self, token: str, public_key: str
    ) -> DecodedAccessTokenPayload:
        payload = jwt.decode(token, public_key, algorithms=[_ALGORITHM])
        if not _is_decoded_access_token_payload(payload):
            raise jwt.InvalidTokenError("Invalid access token payload")
        return payload

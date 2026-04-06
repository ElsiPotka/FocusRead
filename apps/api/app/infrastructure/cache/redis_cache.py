from __future__ import annotations

import gzip
import json
from typing import TYPE_CHECKING, Any

from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from redis.asyncio import Redis

COMPRESSED_PAYLOAD_PREFIX = b"gz:"


class RedisCache:
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def get_bytes(self, key: str) -> bytes | None:
        value = await self._client.get(key)
        if value is None:
            return None
        return bytes(value)

    async def set_bytes(
        self,
        key: str,
        value: bytes,
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        await self._client.set(
            key,
            value,
            ex=ttl_seconds or settings.CACHE_DEFAULT_TTL_SECONDS,
        )

    async def get_json(self, key: str) -> Any | None:
        payload = await self.get_bytes(key)
        if payload is None:
            return None

        if payload.startswith(COMPRESSED_PAYLOAD_PREFIX):
            payload = gzip.decompress(payload.removeprefix(COMPRESSED_PAYLOAD_PREFIX))

        return json.loads(payload.decode("utf-8"))

    async def set_json(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int | None = None,
        compress: bool = False,
    ) -> None:
        payload = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if compress:
            payload = COMPRESSED_PAYLOAD_PREFIX + gzip.compress(payload)

        await self.set_bytes(key, payload, ttl_seconds=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def touch(self, key: str, *, ttl_seconds: int | None = None) -> None:
        await self._client.expire(
            key, ttl_seconds or settings.CACHE_DEFAULT_TTL_SECONDS
        )

from __future__ import annotations

import asyncio

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

_hasher = PasswordHash((Argon2Hasher(),))

DUMMY_HASH = _hasher.hash("dummy-password-for-timing-protection")


async def hash_password(raw: str) -> str:
    return await asyncio.to_thread(_hasher.hash, raw)


async def verify_password(raw: str, hashed: str) -> bool:
    return await asyncio.to_thread(_hasher.verify, raw, hashed)


async def dummy_verify() -> None:
    await asyncio.to_thread(_hasher.verify, "dummy", DUMMY_HASH)

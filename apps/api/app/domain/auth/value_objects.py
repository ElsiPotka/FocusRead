from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID, uuid7


@dataclass(frozen=True, slots=True)
class UserId:
    value: UUID

    @classmethod
    def generate(cls) -> UserId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized:
            raise ValueError("Email is required.")
        if len(normalized) > 320:
            raise ValueError("Email must be 320 characters or less.")
        if not _EMAIL_RE.match(normalized):
            raise ValueError("Invalid email format.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class HashedPassword:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Hashed password cannot be empty.")


@dataclass(frozen=True, slots=True)
class RawPassword:
    value: str

    def __post_init__(self) -> None:
        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if len(self.value) > 128:
            raise ValueError("Password must be 128 characters or less.")


@dataclass(frozen=True, slots=True)
class RefreshTokenHash:
    value: str

    def __post_init__(self) -> None:
        if not self.value or len(self.value) != 64:
            raise ValueError("Invalid refresh token hash.")


_VALID_PROVIDERS = frozenset({"credential", "google", "apple"})


@dataclass(frozen=True, slots=True)
class ProviderId:
    value: str

    def __post_init__(self) -> None:
        if self.value not in _VALID_PROVIDERS:
            raise ValueError(f"Invalid provider: {self.value}")


@dataclass(frozen=True, slots=True)
class AccountId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Account ID is required.")

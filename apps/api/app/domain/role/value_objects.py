from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid7


@dataclass(frozen=True, slots=True)
class RoleId:
    value: UUID

    @classmethod
    def generate(cls) -> RoleId:
        return cls(value=uuid7())

    def __str__(self) -> str:
        return str(self.value)


class RoleName(StrEnum):
    ADMIN = "Admin"
    MERCHANT = "Merchant"
    CLIENT = "Client"

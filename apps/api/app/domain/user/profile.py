from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.account.entities import Account
    from app.domain.role.entities import Role
    from app.domain.user.entities import User


@dataclass(frozen=True, slots=True)
class UserProfile:
    user: User
    accounts: tuple[Account, ...] = field(default_factory=tuple)
    roles: tuple[Role, ...] = field(default_factory=tuple)

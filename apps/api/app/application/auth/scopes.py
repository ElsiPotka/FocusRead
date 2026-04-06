from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.role.value_objects import RoleName

if TYPE_CHECKING:
    from collections.abc import Iterable

    from app.domain.role.entities import Role


def build_access_token_scopes(roles: Iterable[Role]) -> list[str]:
    granted_role_names = {role.name for role in roles}
    return [
        "me",
        *[role_name.value for role_name in RoleName if role_name in granted_role_names],
    ]

from __future__ import annotations

from app.domain.role.entities import Role
from app.domain.role.value_objects import RoleName


class TestRoleCreate:
    def test_create_sets_role_fields(self):
        role = Role.create(
            name=RoleName.CLIENT,
            description="Default client access",
        )

        assert role.name is RoleName.CLIENT
        assert role.description == "Default client access"

    def test_role_equality_uses_identity(self):
        role = Role.create(
            name=RoleName.ADMIN,
            description="Admin access",
        )
        same = Role(
            id=role.id,
            name=RoleName.ADMIN,
            description="Different description",
            created_at=role.created_at,
            updated_at=role.updated_at,
        )

        assert role == same

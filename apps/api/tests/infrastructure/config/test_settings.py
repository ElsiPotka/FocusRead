from __future__ import annotations

from app.infrastructure.config.settings import Settings


class TestSettings:
    def test_local_does_not_force_secure_auth_cookies(self):
        settings = Settings(POSTGRES_PASSWORD="local-password")

        assert settings.AUTH_COOKIE_SECURE is False
        assert settings.AUTH_COOKIE_SECURE_RESOLVED is False

    def test_explicit_override_enables_secure_auth_cookies(self):
        settings = Settings(
            POSTGRES_PASSWORD="local-password",
            AUTH_COOKIE_SECURE=True,
        )

        assert settings.AUTH_COOKIE_SECURE_RESOLVED is True

    def test_production_forces_secure_auth_cookies_even_with_debug_enabled(self):
        settings = Settings(
            ENVIRONMENT="production",
            DEBUG=True,
            POSTGRES_PASSWORD="production-password",
        )

        assert settings.AUTH_COOKIE_SECURE is False
        assert settings.AUTH_COOKIE_SECURE_RESOLVED is True

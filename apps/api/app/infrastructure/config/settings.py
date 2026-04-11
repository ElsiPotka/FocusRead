import warnings
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal, Self
from urllib.parse import quote

from pydantic import (
    Field,
    PostgresDsn,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _parse_list_env_value(
    value: str | list[str] | None,
    *,
    default_if_empty: list[str],
) -> list[str]:
    if value is None or value == "":
        return default_if_empty
    if isinstance(value, list):
        return value
    if value.startswith("["):
        import json

        return json.loads(value)
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables can be set via .env file or system environment.
    All settings are validated at startup to ensure correct configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = Field(
        default="FocusRead API",
        description="The name of the application",
    )

    APP_VERSION: str = Field(
        default="0.1.0",
        description="Semantic version of the application",
    )

    ENVIRONMENT: Literal["local", "test", "staging", "production"] = Field(
        default="local",
        description="Current environment (local, test, staging, or production)",
    )

    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode for detailed error messages",
    )

    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="Prefix for API v1 endpoints",
    )

    REQUEST_ID_MAX_LENGTH: int = Field(
        default=100,
        description="Maximum length for X-Request-ID header",
    )

    API_RATE_LIMIT_DEFAULT: str = Field(
        default="80/minute",
        description="Default rate limit string for SlowAPI (e.g. '80/minute')",
    )

    @computed_field
    @property
    def IS_PRODUCTION(self) -> bool:
        return self.ENVIRONMENT == "production" and not self.DEBUG

    @computed_field
    @property
    def IS_BEHIND_PROXY(self) -> bool:
        return self.ENVIRONMENT in {"staging", "production"}

    STORAGE_BACKEND: Literal["local", "supabase"] = Field(
        default="local",
        description="File storage backend — 'local' or 'supabase'",
    )

    BASE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent,
        description="Base directory of the project",
    )

    STORAGE_DIR: Path = Field(
        default_factory=lambda: (
            Path(__file__).resolve().parent.parent.parent / "storage"
        ),
        description="Directory for local file storage (logs, uploads)",
    )

    UPLOADS_DIR: Path = Field(
        default_factory=lambda: (
            Path(__file__).resolve().parent.parent.parent / "storage" / "uploads"
        ),
        description="Directory for uploaded PDF files",
    )

    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default=[],
        description="Allowed CORS origins (comma-separated in .env or JSON array)",
    )

    ALLOWED_HOSTS: Annotated[list[str], NoDecode] = Field(
        default=["*"],
        description="Allowed hosts for TrustedHostMiddleware (comma-separated)",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str] | None) -> list[str]:
        return _parse_list_env_value(
            value,
            default_if_empty=["http://localhost:3000", "http://127.0.0.1:3000"],
        )

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: str | list[str] | None) -> list[str]:
        return _parse_list_env_value(value, default_if_empty=["*"])

    DB_EAGER_CONNECT: bool = Field(
        default=False,
        description="Verify database connectivity on startup",
    )

    DB_ECHO: bool = Field(
        default=False,
        description="Echo SQL statements to log (never in production)",
    )

    DB_POOL_SIZE: int = Field(
        default=5,
        description="Number of persistent connections in the SQLAlchemy pool",
    )

    DB_MAX_OVERFLOW: int = Field(
        default=10,
        description="Max additional connections beyond pool_size under load",
    )

    USE_PGBOUNCER: bool = Field(
        default=False,
        description=(
            "When true, use NullPool and disable prepared statements "
            "for PgBouncer transaction-level pooling compatibility"
        ),
    )

    POSTGRES_SERVER: str = Field(
        default="127.0.0.1",
        description="PostgreSQL server hostname or IP address",
    )

    POSTGRES_PORT: int = Field(
        default=5432,
        description="PostgreSQL server port",
    )

    POSTGRES_USER: str = Field(
        default="focusread",
        description="PostgreSQL database username",
    )

    POSTGRES_PASSWORD: str = Field(
        default="change_me",
        description="PostgreSQL database password",
    )

    POSTGRES_DB: str = Field(
        default="focusread",
        description="PostgreSQL database name",
    )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    REDIS_EAGER_CONNECT: bool = Field(
        default=False,
        description="Verify Redis connectivity on startup",
    )

    CACHE_DEFAULT_TTL_SECONDS: int = Field(
        default=1800,
        description="Default cache TTL in seconds (30 minutes)",
    )

    REDIS_HOST: str = Field(
        default="127.0.0.1",
        description="Redis server hostname or IP address",
    )

    REDIS_PORT: int = Field(
        default=6379,
        description="Redis server port",
    )

    REDIS_PASSWORD: str = Field(
        default="",
        description="Redis password (empty for local development)",
    )

    REDIS_CACHE_DB: int = Field(
        default=0,
        description="Redis database index for cache",
    )

    REDIS_CELERY_BROKER_DB: int = Field(
        default=1,
        description="Redis database index for Celery broker",
    )

    REDIS_CELERY_RESULT_DB: int = Field(
        default=2,
        description="Redis database index for Celery result backend",
    )

    REDIS_KEY_PREFIX: str = Field(
        default="focusread",
        description="Prefix for all Redis keys",
    )

    def _build_redis_url(self, db: int) -> str:
        password = quote(self.REDIS_PASSWORD, safe="")
        credentials = f":{password}@" if password else ""
        return f"redis://{credentials}{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return self._build_redis_url(self.REDIS_CACHE_DB)

    @computed_field
    @property
    def CELERY_BROKER_URL(self) -> str:
        return self._build_redis_url(self.REDIS_CELERY_BROKER_DB)

    @computed_field
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self._build_redis_url(self.REDIS_CELERY_RESULT_DB)

    CELERY_TASK_ALWAYS_EAGER: bool = Field(
        default=False,
        description="Run Celery tasks synchronously (True for testing only)",
    )

    CELERY_TASK_TIME_LIMIT: int = Field(
        default=1800,
        description="Hard time limit for Celery tasks in seconds (30 minutes)",
    )

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15,
        description="Access token expiration time in minutes",
    )

    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time in days",
    )

    JWT_KEY_PAIR_CACHE_TTL_SECONDS: int = Field(
        default=86400,
        description="TTL for cached RSA key pair in Redis (24 hours)",
    )

    GOOGLE_CLIENT_ID: str = Field(
        default="",
        description="Google OAuth2 client ID",
    )

    GOOGLE_CLIENT_SECRET: str = Field(
        default="",
        description="Google OAuth2 client secret",
    )

    APPLE_CLIENT_ID: str = Field(
        default="",
        description="Apple OAuth2 client ID (Services ID)",
    )

    APPLE_CLIENT_SECRET: str = Field(
        default="",
        description="Apple OAuth2 client secret",
    )

    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for OAuth redirects",
    )

    AUTH_COOKIE_SECURE: bool = Field(
        default=False,
        description=(
            "Force the Secure flag on auth cookies in every environment. "
            "Production always resolves to secure cookies even when this is false."
        ),
    )

    @computed_field
    @property
    def AUTH_COOKIE_SECURE_RESOLVED(self) -> bool:
        return self.AUTH_COOKIE_SECURE or self.ENVIRONMENT == "production"

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        """Raise in non-local envs or warn in local if a secret is still the placeholder."""
        if value == "change_me":
            message = (
                f'The value of {var_name} is "change_me". '
                "For security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        return self

    def with_environment(self, environment: str) -> Self:
        return self.model_copy(update={"ENVIRONMENT": environment})


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

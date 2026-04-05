from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, computed_field, field_validator
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
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = Field(default="FocusRead API")
    APP_VERSION: str = Field(default="0.1.0")
    ENVIRONMENT: Literal["local", "test", "staging", "production"] = Field(
        default="local"
    )
    DEBUG: bool = Field(default=False)
    API_V1_PREFIX: str = Field(default="/api/v1")
    REQUEST_ID_MAX_LENGTH: int = Field(default=100)
    API_RATE_LIMIT_DEFAULT: str = Field(default="80/minute")

    STORAGE_BACKEND: Literal["local", "supabase"] = Field(default="local")

    BASE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
    )

    STORAGE_DIR: Path = Field(
        default_factory=lambda: (
            Path(__file__).resolve().parent.parent.parent / "storage"
        )
    )

    UPLOADS_DIR: Path = Field(
        default_factory=lambda: (
            Path(__file__).resolve().parent.parent.parent / "storage" / "uploads"
        )
    )

    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(default=[])
    ALLOWED_HOSTS: Annotated[list[str], NoDecode] = Field(default=["*"])

    DB_EAGER_CONNECT: bool = Field(default=False)
    DB_ECHO: bool = Field(default=False)

    POSTGRES_SERVER: str = Field(default="127.0.0.1")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="focusread")
    POSTGRES_PASSWORD: str = Field(default="focusread")
    POSTGRES_DB: str = Field(default="focusread")

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

    @computed_field
    @property
    def IS_PRODUCTION(self) -> bool:
        return self.ENVIRONMENT == "production" and not self.DEBUG

    @computed_field
    @property
    def IS_BEHIND_PROXY(self) -> bool:
        return self.ENVIRONMENT in {"staging", "production"}

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def with_environment(self, environment: str) -> Self:
        return self.model_copy(update={"ENVIRONMENT": environment})


settings = Settings()

from __future__ import annotations

from datetime import UTC, datetime

from app.domain.auth.value_objects import RefreshTokenHash, UserId


class Session:
    def __init__(
        self,
        *,
        id: UserId,
        user_id: UserId,
        token_hash: RefreshTokenHash,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._user_id = user_id
        self._token_hash = token_hash
        self._expires_at = expires_at
        self._user_agent = user_agent
        self._ip_address = ip_address
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(
        cls,
        *,
        user_id: UserId,
        token_hash: RefreshTokenHash,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> Session:
        return cls(
            id=UserId.generate(),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

    @property
    def id(self) -> UserId:
        return self._id

    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def token_hash(self) -> RefreshTokenHash:
        return self._token_hash

    @property
    def expires_at(self) -> datetime:
        return self._expires_at

    @property
    def user_agent(self) -> str | None:
        return self._user_agent

    @property
    def ip_address(self) -> str | None:
        return self._ip_address

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) > self._expires_at

    def rotate(
        self, new_token_hash: RefreshTokenHash, new_expires_at: datetime
    ) -> None:
        self._token_hash = new_token_hash
        self._expires_at = new_expires_at
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Session) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

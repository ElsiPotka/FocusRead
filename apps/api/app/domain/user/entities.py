from __future__ import annotations

from datetime import UTC, datetime

from app.domain.auth.value_objects import Email, UserId


class User:
    def __init__(
        self,
        *,
        id: UserId,
        name: str,
        surname: str,
        email: Email,
        email_verified: bool = False,
        image: str | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id = id
        self._name = name
        self._surname = surname
        self._email = email
        self._email_verified = email_verified
        self._image = image
        self._is_active = is_active
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @classmethod
    def create(cls, *, name: str, surname: str, email: Email) -> User:
        return cls(
            id=UserId.generate(),
            name=name,
            surname=surname,
            email=email,
        )

    @property
    def id(self) -> UserId:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def surname(self) -> str:
        return self._surname

    @property
    def email(self) -> Email:
        return self._email

    @property
    def email_verified(self) -> bool:
        return self._email_verified

    @property
    def image(self) -> str | None:
        return self._image

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def full_name(self) -> str:
        return f"{self._name} {self._surname}".strip()

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def verify_email(self) -> None:
        self._email_verified = True
        self._updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        self._is_active = False
        self._updated_at = datetime.now(UTC)

    def update_profile(
        self,
        *,
        name: str | None = None,
        surname: str | None = None,
        image: str | None = None,
    ) -> None:
        if name is not None:
            self._name = name
        if surname is not None:
            self._surname = surname
        if image is not None:
            self._image = image
        self._updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, User) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

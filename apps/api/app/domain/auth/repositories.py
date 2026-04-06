from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.domain.account.entities import Account
    from app.domain.auth.value_objects import (
        Email,
        ProviderId,
        RefreshTokenHash,
        UserId,
    )
    from app.domain.session.entities import Session
    from app.domain.user.entities import User
    from app.domain.user.profile import UserProfile


class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None: ...

    @abstractmethod
    async def get(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None: ...

    @abstractmethod
    async def get_profile(self, user_id: UserId) -> UserProfile | None: ...

    @abstractmethod
    async def paginate_profiles(
        self,
        *,
        page: int,
        per_page: int,
        cursor: str | None = None,
    ) -> dict[str, Any]: ...


class AccountRepository(ABC):
    @abstractmethod
    async def save(self, account: Account) -> None: ...

    @abstractmethod
    async def get_by_provider(
        self, provider_id: ProviderId, account_id: str
    ) -> Account | None: ...

    @abstractmethod
    async def get_credential_by_user(self, user_id: UserId) -> Account | None: ...


class SessionRepository(ABC):
    @abstractmethod
    async def save(self, session: Session) -> None: ...

    @abstractmethod
    async def get_by_token_hash(
        self, token_hash: RefreshTokenHash
    ) -> Session | None: ...

    @abstractmethod
    async def delete(self, session_id: UserId) -> None: ...

    @abstractmethod
    async def delete_all_for_user(self, user_id: UserId) -> None: ...


class JWTSigningKeyRepository(ABC):
    @abstractmethod
    async def save_key_pair(
        self,
        *,
        public_key: str,
        private_key: str,
        algorithm: str,
    ) -> None: ...

    @abstractmethod
    async def get_active_key_pair(self) -> tuple[str, str] | None: ...

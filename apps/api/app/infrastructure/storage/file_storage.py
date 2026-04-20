from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.infrastructure.config.settings import settings

if TYPE_CHECKING:
    from pathlib import Path


class FileStorage(ABC):
    """Asset-oriented blob storage.

    Speaks in `storage_key` (a logical, asset-owned identifier) rather than
    mutable book file paths. Deletion semantics target the asset blob, not
    the catalog book record.
    """

    @abstractmethod
    async def store(self, *, storage_key: str, content: bytes) -> None: ...

    @abstractmethod
    async def delete(self, *, storage_key: str) -> None: ...

    @abstractmethod
    def resolve_path(self, *, storage_key: str) -> str:
        """Resolve a storage_key to a backend-native locator.

        For local backends, returns an absolute filesystem path consumers
        (e.g. the PDF processor) can open directly. Remote backends may
        return a pre-signed URL or a downloaded temp path.
        """


class LocalFileStorage(FileStorage):
    def __init__(self, uploads_dir: Path) -> None:
        self._uploads_dir = uploads_dir

    async def store(self, *, storage_key: str, content: bytes) -> None:
        full_path = self._uploads_dir / storage_key
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)

    async def delete(self, *, storage_key: str) -> None:
        (self._uploads_dir / storage_key).unlink(missing_ok=True)

    def resolve_path(self, *, storage_key: str) -> str:
        return str(self._uploads_dir / storage_key)


def get_file_storage() -> FileStorage:
    return LocalFileStorage(settings.UPLOADS_DIR)

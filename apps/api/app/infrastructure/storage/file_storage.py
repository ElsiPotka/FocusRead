from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.infrastructure.config.settings import settings


class FileStorage(ABC):
    @abstractmethod
    async def save_upload(self, *, file_content: bytes, destination: str) -> str: ...

    @abstractmethod
    async def delete_file(self, *, file_path: str) -> None: ...


class LocalFileStorage(FileStorage):
    def __init__(self, uploads_dir: Path) -> None:
        self._uploads_dir = uploads_dir

    async def save_upload(self, *, file_content: bytes, destination: str) -> str:
        full_path = self._uploads_dir / destination
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(file_content)
        return str(full_path)

    async def delete_file(self, *, file_path: str) -> None:
        Path(file_path).unlink(missing_ok=True)


def get_file_storage() -> FileStorage:
    return LocalFileStorage(settings.UPLOADS_DIR)

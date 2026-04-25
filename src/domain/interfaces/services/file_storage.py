from typing import Protocol

from domain.entities.base import Url


class FileStorage(Protocol):
    async def upload_file(self, *, file_bytes: bytes, destination_path: str, content_type: str) -> Url:
        pass

from typing import Protocol

from domain.entities.base import Url


class FileStorage(Protocol):
    def upload_file(self, *, file_bytes: bytes,
                    destination_path: str,
                    content_type: str) -> Url:
        pass

    def delete(self, *, file_path: str) -> None:
        pass



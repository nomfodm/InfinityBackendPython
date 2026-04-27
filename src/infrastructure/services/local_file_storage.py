import asyncio
import os

from domain.entities.base import Url


class LocalFileStorage:
    def __init__(self, *, base_dir: str, public_base_url: str) -> None:
        self._base_dir = base_dir
        self._public_base_url = public_base_url.rstrip("/")

    async def upload_file(self, *, file_bytes: bytes, destination_path: str, content_type: str) -> Url:
        full_path = os.path.join(self._base_dir, destination_path)
        await asyncio.to_thread(self._write, full_path, file_bytes)
        return Url(f"{self._public_base_url}/{destination_path}")

    @staticmethod
    def _write(path: str, data: bytes) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)

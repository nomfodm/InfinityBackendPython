from typing import Protocol

from domain.entities.wardrobe import TextureType


class TextureService(Protocol):
    def validate_texture(self, *, file_bytes: bytes, texture_type: TextureType) -> None:
        pass

    def generate_3d_head_from_skin(self, *, skin_bytes: bytes, size: int = 128) -> bytes:
        pass

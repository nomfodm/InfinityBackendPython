from typing import Protocol

from domain.entities.wardrobe import SkinModel, TextureType


class TextureService(Protocol):
    def validate_texture(self, *, file_bytes: bytes, texture_type: TextureType) -> None:
        pass

    def generate_3d_head_from_skin(self, *, skin_bytes: bytes, size: int = 128) -> bytes:
        pass

    def detect_skin_model(self, *, skin_bytes: bytes) -> SkinModel:
        pass

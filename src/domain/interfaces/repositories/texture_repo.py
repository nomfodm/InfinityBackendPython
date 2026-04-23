from typing import Protocol

from domain.entities.wardrobe import Texture


class TextureRepository(Protocol):
    async def get_texture_by_hash(self, *, hash_sha256: str) -> Texture | None:
        pass

    async def save(self, *, texture: Texture) -> Texture:
        pass

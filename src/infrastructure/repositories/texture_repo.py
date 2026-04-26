from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.wardrobe import Texture
from domain.interfaces.repositories.texture_repo import TextureRepository
from infrastructure.database.models.wardrobe_model import TextureModel


class SqlTextureRepository(TextureRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_texture_by_hash(self, hash_sha256: str) -> Texture | None:
        result = await self._session.execute(select(TextureModel).where(TextureModel.hash == hash_sha256))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def save(self, texture: Texture) -> Texture:
        merged = await self._session.merge(TextureModel.from_domain(texture))
        await self._session.flush()
        return merged.to_domain()

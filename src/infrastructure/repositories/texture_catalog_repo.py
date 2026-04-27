from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.entities.wardrobe import TextureCatalogItem
from domain.exceptions.wardrobe import TextureCatalogItemNotFoundError
from domain.interfaces.repositories.texture_catalog_repo import TextureCatalogRepository
from infrastructure.database.models.wardrobe_model import TextureCatalogItemModel


class SqlTextureCatalogRepository(TextureCatalogRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: int) -> TextureCatalogItem | None:
        result = await self._session.execute(
            select(TextureCatalogItemModel)
            .where(TextureCatalogItemModel.id == id)
            .options(selectinload(TextureCatalogItemModel.texture))
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_id_or_raise(self, id: int) -> TextureCatalogItem:
        item = await self.get_by_id(id)
        if item is None:
            raise TextureCatalogItemNotFoundError("Такой текстуры нет в каталоге.")
        return item

    async def get_all(self) -> list[TextureCatalogItem]:
        result = await self._session.execute(
            select(TextureCatalogItemModel).options(selectinload(TextureCatalogItemModel.texture))
        )
        return [model.to_domain() for model in result.scalars().all()]

    async def save(self, item: TextureCatalogItem) -> TextureCatalogItem:
        merged = await self._session.merge(TextureCatalogItemModel.from_domain(item))
        await self._session.flush()
        await self._session.refresh(merged, ["texture"])
        return merged.to_domain()

    async def delete(self, item: TextureCatalogItem) -> None:
        await self._session.execute(delete(TextureCatalogItemModel).where(TextureCatalogItemModel.id == item.id))

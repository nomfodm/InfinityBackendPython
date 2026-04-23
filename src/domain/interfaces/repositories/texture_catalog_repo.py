from typing import Protocol

from domain.entities.wardrobe import TextureCatalogItem
from domain.exceptions.wardrobe import TextureCatalogItemNotFoundError


class TextureCatalogRepository(Protocol):
    async def get_by_id(self, *, id: int) -> TextureCatalogItem | None:
        pass

    async def get_by_id_or_raise(self, *, id: int) -> TextureCatalogItem:
        texture_cat_item = await self.get_by_id(id=id)
        if not texture_cat_item:
            raise TextureCatalogItemNotFoundError("Такой текстуры нет в каталоге.")
        return texture_cat_item

    async def save(self, *, item: TextureCatalogItem) -> TextureCatalogItem:
        pass

    async def delete(self, *, item: TextureCatalogItem) -> None:
        pass

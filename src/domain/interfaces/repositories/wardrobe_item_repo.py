from typing import Protocol

from domain.entities.wardrobe import WardrobeItem
from domain.exceptions.wardrobe import WardrobeItemNotFoundError


class WardrobeItemRepository(Protocol):
    async def get_by_id_from_user_wardrobe(self, *, id: int, user_id: int) -> WardrobeItem | None:
        pass

    async def get_by_id_from_user_wardrobe_or_raise(self, *, id: int, user_id: int) -> WardrobeItem:
        item = await self.get_by_id_from_user_wardrobe(id=id, user_id=user_id)
        if item is None:
            raise WardrobeItemNotFoundError("Предмет гардероба не найден.")
        return item

    async def save(self, *, item: WardrobeItem) -> WardrobeItem:
        pass

    async def delete(self, *, item: WardrobeItem) -> None:
        pass

    async def get_user_wardrobe(self, *, user_id: int) -> list[WardrobeItem]:
        pass




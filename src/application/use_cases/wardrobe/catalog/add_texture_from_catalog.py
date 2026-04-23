import datetime
from dataclasses import dataclass
from datetime import UTC

from application.decorators.auth import require_login
from application.dtos.wardrobe import WardrobeItemResponse
from domain.entities.user import User
from domain.entities.wardrobe import WardrobeItem
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class AddTextureFromCatalogRequest:
    id: int


class AddTextureFromCatalogUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    async def execute(self, *, dto: AddTextureFromCatalogRequest, user: User) -> WardrobeItemResponse:
        async with self._uow:
            catalog_item = await self._uow.texture_catalog.get_by_id_or_raise(id=dto.id)

            wardrobe_item = await self._uow.wardrobe.save(
                item=WardrobeItem(
                    user_id=user.id,
                    texture=catalog_item.texture,
                    author_id=catalog_item.author_id,
                    acquired_at=datetime.datetime.now(UTC),
                    label=catalog_item.title,
                )
            )

            await self._uow.commit()
            return WardrobeItemResponse.from_domain(wardrobe_item)

import datetime
from dataclasses import dataclass
from datetime import UTC

from application.decorators.auth import require_login
from application.dtos.wardrobe import TextureCatalogItemResponse
from domain.entities.base import ContentLabel
from domain.entities.user import User
from domain.entities.wardrobe import TextureCatalogItem
from domain.exceptions.wardrobe import CannotPublishAddedTextureError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass
class PublishTextureRequest:
    wardrobe_item_id: int
    title: ContentLabel


class PublishTextureUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    async def execute(self, *, dto: PublishTextureRequest, user: User) -> TextureCatalogItemResponse:
        async with self._uow:
            wardrobe_item = await self._uow.wardrobe.get_by_id_from_user_wardrobe_or_raise(id=dto.wardrobe_item_id, user_id=user.id)
            if wardrobe_item.author_id != user.id:
                raise CannotPublishAddedTextureError("Нельзя публиковать текстуру, которую вы добавили из каталога.")

            published_texture = await self._uow.texture_catalog.save(item=TextureCatalogItem(
                texture=wardrobe_item.texture,
                author_id=user.id,
                published_at=datetime.datetime.now(UTC),
                title=dto.title
            ))

            await self._uow.commit()

            return TextureCatalogItemResponse.from_domain(published_texture)





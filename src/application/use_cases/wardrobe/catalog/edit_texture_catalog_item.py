from dataclasses import dataclass

from application.decorators.auth import require_login
from application.dtos.wardrobe import TextureCatalogItemResponse
from domain.entities.base import ContentLabel
from domain.entities.user import User
from domain.exceptions.auth import AccessDeniedError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass
class EditTextureCatalogItemRequest:
    id: int
    title: ContentLabel


class EditTextureCatalogItemUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    async def execute(self, *, dto: EditTextureCatalogItemRequest, user: User) -> TextureCatalogItemResponse:
        async with self._uow:
            item = await self._uow.texture_catalog.get_by_id_or_raise(id=dto.id)
            if item.author_id != user.id:
                raise AccessDeniedError("Это не ваша текстура.")

            item.title = dto.title
            edited = await self._uow.texture_catalog.save(item=item)

            await self._uow.commit()
            return TextureCatalogItemResponse.from_domain(edited)

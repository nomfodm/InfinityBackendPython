from dataclasses import dataclass

from application.decorators.auth import require_login, require_not_banned
from application.dtos.common import StatusResponse
from domain.entities.user import User
from domain.exceptions.auth import AccessDeniedError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass
class UnpublishTextureRequest:
    id: int


class UnpublishTextureUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @require_not_banned
    async def execute(self, *, dto: UnpublishTextureRequest, user: User) -> StatusResponse:
        async with self._uow:
            item = await self._uow.texture_catalog.get_by_id_or_raise(id=dto.id)
            if item.author_id != user.id:
                raise AccessDeniedError("Эта текстура опубликована другим пользователем.")

            wardrobe_ids_to_delete = await self._uow.wardrobe.get_ids_by_texture_id_except_user(
                texture_id=item.texture.id, except_user_id=user.id
            )
            if wardrobe_ids_to_delete:
                await self._uow.minecraft_profiles.clear_active_cosmetics_for_wardrobe_items(
                    wardrobe_item_ids=wardrobe_ids_to_delete
                )
                await self._uow.wardrobe.delete_by_texture_id_except_user(
                    texture_id=item.texture.id, except_user_id=user.id
                )

            await self._uow.texture_catalog.delete(item=item)

            await self._uow.commit()
            return StatusResponse()

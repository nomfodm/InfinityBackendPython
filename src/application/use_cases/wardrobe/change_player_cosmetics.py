from dataclasses import dataclass

from application.decorators.auth import require_login
from application.dtos.common import StatusResponse
from domain.entities.user import User
from domain.entities.wardrobe import TextureType
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ChangePlayerCosmeticsRequest:
    item_id: int


class ChangePlayerCosmeticsUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    async def execute(self, *, dto: ChangePlayerCosmeticsRequest, user: User) -> StatusResponse:
        async with self._uow:
            wardrobe_item = await self._uow.wardrobe.get_by_id_from_user_wardrobe_or_raise(
                id=dto.item_id, user_id=user.id
            )
            mc_profile = await self._uow.minecraft_profiles.get_by_user_id_or_raise(user_id=user.id)

            if wardrobe_item.texture.type == TextureType.SKIN:
                mc_profile.active_skin_id = wardrobe_item.id
            elif wardrobe_item.texture.type == TextureType.CAPE:
                mc_profile.active_cape_id = wardrobe_item.id

            await self._uow.minecraft_profiles.save(profile=mc_profile)

            await self._uow.commit()
            return StatusResponse()

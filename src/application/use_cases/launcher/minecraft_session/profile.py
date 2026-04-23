from dataclasses import dataclass
from uuid import UUID

from application.dtos.minecraft_session import ProfileResponse
from application.services.minecraft_profile import MinecraftProfileService
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ProfileRequest:
    uuid: UUID


class ProfileUseCase:
    def __init__(self, *, uow: UnitOfWork, mc_profile_service: MinecraftProfileService):
        self._uow = uow
        self._mc_profile_service = mc_profile_service

    async def execute(self, *, dto: ProfileRequest) -> ProfileResponse:
        async with self._uow:
            mc_profile = await self._uow.minecraft_profiles.get_by_uuid_or_raise(uuid=dto.uuid)
            response = self._mc_profile_service.build_profile_response(
                mc_profile=mc_profile,
                skin_wardrobe_item=await self._uow.wardrobe.get_by_id_from_user_wardrobe_or_raise(
                    id=mc_profile.active_skin_id, user_id=mc_profile.user_id
                )
                if mc_profile.active_skin_id is not None
                else None,
                cape_wardrobe_item=await self._uow.wardrobe.get_by_id_from_user_wardrobe_or_raise(
                    id=mc_profile.active_cape_id, user_id=mc_profile.user_id
                )
                if mc_profile.active_cape_id is not None
                else None,
            )

            return response

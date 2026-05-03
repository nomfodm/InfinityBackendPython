import uuid
from typing import Protocol

from domain.entities.base import UserRelatedHandle
from domain.entities.minecraft_profile import MinecraftProfile
from domain.exceptions.minecraft import MinecraftProfileNotFoundError


class MinecraftProfileRepository(Protocol):
    async def save(self, *, profile: MinecraftProfile) -> MinecraftProfile:
        pass

    async def get_by_user_id(self, *, user_id: int) -> MinecraftProfile | None:
        pass

    async def get_by_user_id_or_raise(self, *, user_id: int) -> MinecraftProfile:
        mc_profile = await self.get_by_user_id(user_id=user_id)
        if mc_profile is None:
            raise MinecraftProfileNotFoundError("По непонятной причине, профиля для этого пользователя нет.")
        return mc_profile

    async def get_by_uuid(self, *, uuid: uuid.UUID) -> MinecraftProfile | None:
        pass

    async def get_by_uuid_or_raise(self, *, uuid: uuid.UUID) -> MinecraftProfile:
        mc_profile = await self.get_by_uuid(uuid=uuid)
        if mc_profile is None:
            raise MinecraftProfileNotFoundError("По непонятной причине, профиля для этого пользователя нет.")
        return mc_profile

    async def get_by_nickname(self, *, nickname: UserRelatedHandle) -> MinecraftProfile | None:
        pass

    async def get_by_nickname_or_raise(self, *, nickname: UserRelatedHandle) -> MinecraftProfile:
        mc_profile = await self.get_by_nickname(nickname=nickname)
        if mc_profile is None:
            raise MinecraftProfileNotFoundError("По непонятной причине, профиля для этого пользователя нет.")
        return mc_profile

    async def clear_active_cosmetics_for_wardrobe_items(self, *, wardrobe_item_ids: list[int]) -> None:
        pass

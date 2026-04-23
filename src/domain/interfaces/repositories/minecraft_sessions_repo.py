from typing import Protocol
from uuid import UUID

from domain.entities.minecraft_session import MinecraftSession
from domain.exceptions.minecraft import MinecraftSessionNotFoundError


class MinecraftSessionRepository(Protocol):
    async def save(self, *, mc_session: MinecraftSession) -> MinecraftSession:
        pass

    async def get_by_profile_uuid(self, *, profile_uuid: UUID) -> MinecraftSession | None:
        pass

    async def get_by_profile_uuid_or_raise(self, *, profile_uuid: UUID) -> MinecraftSession:
        mc_session = await self.get_by_profile_uuid(profile_uuid=profile_uuid)
        if mc_session is None:
            raise MinecraftSessionNotFoundError("Игровой сессии для этого пользователя нет.")
        return mc_session




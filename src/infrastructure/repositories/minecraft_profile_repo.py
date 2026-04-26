import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.base import UserRelatedHandle
from domain.entities.minecraft_profile import MinecraftProfile
from domain.exceptions.minecraft import MinecraftProfileNotFoundError
from domain.interfaces.repositories.minecraft_profile_repo import MinecraftProfileRepository
from infrastructure.database.models.minecraft_profile_model import MinecraftProfileModel


class SqlMinecraftProfileRepository(MinecraftProfileRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, profile: MinecraftProfile) -> MinecraftProfile:
        merged = await self._session.merge(MinecraftProfileModel.from_domain(profile))
        await self._session.flush()
        return merged.to_domain()

    async def get_by_user_id(self, user_id: int) -> MinecraftProfile | None:
        result = await self._session.execute(
            select(MinecraftProfileModel).where(MinecraftProfileModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_user_id_or_raise(self, user_id: int) -> MinecraftProfile:
        profile = await self.get_by_user_id(user_id)
        if profile is None:
            raise MinecraftProfileNotFoundError("По непонятной причине, профиля для этого пользователя нет.")
        return profile

    async def get_by_uuid(self, uuid: uuid.UUID) -> MinecraftProfile | None:
        result = await self._session.execute(select(MinecraftProfileModel).where(MinecraftProfileModel.uuid == uuid))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_uuid_or_raise(self, uuid: uuid.UUID) -> MinecraftProfile:
        profile = await self.get_by_uuid(uuid)
        if profile is None:
            raise MinecraftProfileNotFoundError("По непонятной причине, профиля для этого пользователя нет.")
        return profile

    async def get_by_nickname(self, nickname: UserRelatedHandle) -> MinecraftProfile | None:
        result = await self._session.execute(
            select(MinecraftProfileModel).where(MinecraftProfileModel.nickname == nickname.value)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_nickname_or_raise(self, nickname: UserRelatedHandle) -> MinecraftProfile:
        profile = await self.get_by_nickname(nickname)
        if profile is None:
            raise MinecraftProfileNotFoundError("По непонятной причине, профиля для этого пользователя нет.")
        return profile

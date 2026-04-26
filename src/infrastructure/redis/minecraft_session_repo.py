import json
from uuid import UUID

from redis.asyncio import Redis

from domain.entities.base import MCAccessToken, MCServerID, UserRelatedHandle
from domain.entities.minecraft_session import MinecraftSession
from domain.exceptions.minecraft import MinecraftSessionNotFoundError
from domain.interfaces.repositories.minecraft_session_repo import MinecraftSessionRepository


class RedisMinecraftSessionRepository(MinecraftSessionRepository):
    def __init__(self, client: Redis) -> None:
        self._client = client

    def _key(self, profile_uuid: UUID) -> str:
        return f"mc_session:{profile_uuid}"

    async def save(self, mc_session: MinecraftSession, ttl: int) -> MinecraftSession:
        data = json.dumps(
            {
                "access_token": mc_session.access_token.value,
                "nickname": mc_session.nickname.value,
                "profile_uuid": str(mc_session.profile_uuid),
                "user_id": mc_session.user_id,
                "server_id": mc_session.server_id.value if mc_session.server_id else None,
            }
        )
        await self._client.setex(self._key(mc_session.profile_uuid), ttl, data)
        return mc_session

    async def get_by_profile_uuid(self, profile_uuid: UUID) -> MinecraftSession | None:
        raw = await self._client.get(self._key(profile_uuid))
        if raw is None:
            return None
        d = json.loads(raw)
        return MinecraftSession(
            access_token=MCAccessToken(d["access_token"]),
            nickname=UserRelatedHandle(d["nickname"]),
            profile_uuid=UUID(d["profile_uuid"]),
            user_id=d["user_id"],
            server_id=MCServerID(d["server_id"]) if d["server_id"] else None,
        )

    async def get_by_profile_uuid_or_raise(self, profile_uuid: UUID) -> MinecraftSession:
        mc_session = await self.get_by_profile_uuid(profile_uuid)
        if mc_session is None:
            raise MinecraftSessionNotFoundError("Игровой сессии для этого пользователя нет.")
        return mc_session

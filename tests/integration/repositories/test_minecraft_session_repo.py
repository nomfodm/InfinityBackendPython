from uuid import uuid4

import pytest

from domain.entities.base import MCAccessToken, MCServerID, UserRelatedHandle
from domain.entities.minecraft_session import MinecraftSession
from domain.exceptions.minecraft import MinecraftSessionNotFoundError
from infrastructure.redis.minecraft_session_repo import RedisMinecraftSessionRepository


def make_session(*, with_server_id: bool = False) -> MinecraftSession:
    return MinecraftSession(
        access_token=MCAccessToken("a" * 32),
        nickname=UserRelatedHandle("testplayer"),
        profile_uuid=uuid4(),
        user_id=1,
        server_id=MCServerID("s" * 32) if with_server_id else None,
    )


async def test_save_and_get_returns_session(redis_client):
    repo = RedisMinecraftSessionRepository(redis_client)
    session = make_session()

    await repo.save(mc_session=session, ttl=300)
    result = await repo.get_by_profile_uuid(profile_uuid=session.profile_uuid)

    assert result is not None
    assert result.profile_uuid == session.profile_uuid
    assert result.access_token == session.access_token
    assert result.nickname == session.nickname
    assert result.user_id == session.user_id


async def test_save_with_server_id_none(redis_client):
    repo = RedisMinecraftSessionRepository(redis_client)
    session = make_session(with_server_id=False)

    await repo.save(mc_session=session, ttl=300)
    result = await repo.get_by_profile_uuid(profile_uuid=session.profile_uuid)

    assert result is not None
    assert result.server_id is None


async def test_save_with_server_id_set(redis_client):
    repo = RedisMinecraftSessionRepository(redis_client)
    session = make_session(with_server_id=True)

    await repo.save(mc_session=session, ttl=300)
    result = await repo.get_by_profile_uuid(profile_uuid=session.profile_uuid)

    assert result is not None
    assert result.server_id == session.server_id


async def test_get_returns_none_when_not_found(redis_client):
    repo = RedisMinecraftSessionRepository(redis_client)

    result = await repo.get_by_profile_uuid(profile_uuid=uuid4())

    assert result is None


async def test_get_or_raise_raises_when_not_found(redis_client):
    repo = RedisMinecraftSessionRepository(redis_client)

    with pytest.raises(MinecraftSessionNotFoundError):
        await repo.get_by_profile_uuid_or_raise(profile_uuid=uuid4())

import uuid

import pytest

from domain.entities.base import UserRelatedHandle
from domain.entities.minecraft_profile import MinecraftProfile
from domain.exceptions.minecraft import MinecraftProfileNotFoundError
from infrastructure.repositories.minecraft_profile_repo import SqlMinecraftProfileRepository


def make_profile(user_id: int, nickname: str = "nicktest") -> MinecraftProfile:
    return MinecraftProfile(
        user_id=user_id,
        uuid=uuid.uuid4(),
        nickname=UserRelatedHandle(nickname),
    )


async def test_save_assigns_id(db_session, saved_user):
    repo = SqlMinecraftProfileRepository(db_session)

    saved = await repo.save(make_profile(saved_user.id))

    assert saved.id is not None


async def test_get_by_user_id(db_session, saved_user):
    repo = SqlMinecraftProfileRepository(db_session)
    profile = await repo.save(make_profile(saved_user.id))

    found = await repo.get_by_user_id(saved_user.id)

    assert found is not None
    assert found.id == profile.id


async def test_get_by_user_id_not_found(db_session):
    repo = SqlMinecraftProfileRepository(db_session)

    found = await repo.get_by_user_id(999_999)

    assert found is None


async def test_get_by_user_id_or_raise_not_found(db_session):
    repo = SqlMinecraftProfileRepository(db_session)

    with pytest.raises(MinecraftProfileNotFoundError):
        await repo.get_by_user_id_or_raise(999_999)


async def test_get_by_uuid(db_session, saved_user):
    repo = SqlMinecraftProfileRepository(db_session)
    profile = await repo.save(make_profile(saved_user.id))

    found = await repo.get_by_uuid(profile.uuid)

    assert found is not None
    assert found.id == profile.id


async def test_get_by_nickname(db_session, saved_user):
    repo = SqlMinecraftProfileRepository(db_session)
    profile = await repo.save(make_profile(saved_user.id, nickname="nicktest"))

    found = await repo.get_by_nickname(UserRelatedHandle("nicktest"))

    assert found is not None
    assert found.id == profile.id


async def test_get_by_nickname_or_raise_not_found(db_session):
    repo = SqlMinecraftProfileRepository(db_session)

    with pytest.raises(MinecraftProfileNotFoundError):
        await repo.get_by_nickname_or_raise(UserRelatedHandle("noExist1"))


async def test_save_upserts(db_session, saved_user):
    repo = SqlMinecraftProfileRepository(db_session)
    profile = await repo.save(make_profile(saved_user.id))

    profile.nickname = UserRelatedHandle("newnick1")
    updated = await repo.save(profile)

    assert updated.id == profile.id
    assert updated.nickname.value == "newnick1"

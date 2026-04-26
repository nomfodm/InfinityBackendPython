from datetime import UTC, datetime

import pytest

from domain.entities.base import ContentLabel, Url
from domain.entities.wardrobe import Texture, TextureType, WardrobeItem
from domain.exceptions.wardrobe import WardrobeItemNotFoundError
from infrastructure.repositories.texture_repo import SqlTextureRepository
from infrastructure.repositories.wardrobe_item_repo import SqlWardrobeItemRepository


def make_texture(n: int = 1) -> Texture:
    return Texture(
        hash=f"abc123hash{n:04d}{'x' * 50}",
        type=TextureType.SKIN,
        url=Url(f"https://cdn.example.com/skins/skin{n}.png"),
    )


def make_wardrobe_item(user_id: int, texture: Texture) -> WardrobeItem:
    return WardrobeItem(
        user_id=user_id,
        author_id=user_id,
        texture=texture,
        acquired_at=datetime.now(UTC),
        label=ContentLabel("Cool Skin"),
    )


@pytest.fixture
async def saved_texture(db_session):
    return await SqlTextureRepository(db_session).save(make_texture())


async def test_save_and_get_wardrobe_loads_texture(db_session, saved_user, saved_texture):
    repo = SqlWardrobeItemRepository(db_session)

    item = await repo.save(make_wardrobe_item(saved_user.id, saved_texture))

    assert item.id is not None
    assert item.texture.hash == saved_texture.hash


async def test_get_user_wardrobe(db_session, saved_user, saved_texture):
    repo = SqlWardrobeItemRepository(db_session)
    await repo.save(make_wardrobe_item(saved_user.id, saved_texture))

    wardrobe = await repo.get_user_wardrobe(saved_user.id)

    assert len(wardrobe) == 1
    assert wardrobe[0].texture.url == saved_texture.url


async def test_get_user_wardrobe_empty(db_session, saved_user):
    repo = SqlWardrobeItemRepository(db_session)

    wardrobe = await repo.get_user_wardrobe(saved_user.id)

    assert wardrobe == []


async def test_get_by_id_from_user_wardrobe_found(db_session, saved_user, saved_texture):
    repo = SqlWardrobeItemRepository(db_session)
    item = await repo.save(make_wardrobe_item(saved_user.id, saved_texture))

    found = await repo.get_by_id_from_user_wardrobe(item.id, saved_user.id)

    assert found is not None
    assert found.id == item.id


async def test_get_by_id_from_user_wardrobe_wrong_user(db_session, saved_user, saved_texture):
    repo = SqlWardrobeItemRepository(db_session)
    item = await repo.save(make_wardrobe_item(saved_user.id, saved_texture))

    found = await repo.get_by_id_from_user_wardrobe(item.id, user_id=999_999)

    assert found is None


async def test_get_by_id_from_user_wardrobe_or_raise_not_found(db_session, saved_user):
    repo = SqlWardrobeItemRepository(db_session)

    with pytest.raises(WardrobeItemNotFoundError):
        await repo.get_by_id_from_user_wardrobe_or_raise(999_999, saved_user.id)


async def test_delete_removes_item(db_session, saved_user, saved_texture):
    repo = SqlWardrobeItemRepository(db_session)
    item = await repo.save(make_wardrobe_item(saved_user.id, saved_texture))

    await repo.delete(item)

    assert await repo.get_by_id_from_user_wardrobe(item.id, saved_user.id) is None

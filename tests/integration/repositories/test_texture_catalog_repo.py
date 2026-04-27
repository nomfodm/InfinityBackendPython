from datetime import UTC, datetime

import pytest

from domain.entities.base import ContentLabel, Url
from domain.entities.wardrobe import Texture, TextureCatalogItem, TextureType
from infrastructure.repositories.texture_catalog_repo import SqlTextureCatalogRepository
from infrastructure.repositories.texture_repo import SqlTextureRepository


def make_texture(n: int = 1) -> Texture:
    return Texture(
        hash=f"abc123hash{n:04d}{'x' * 50}",
        type=TextureType.SKIN,
        url=Url(f"https://cdn.example.com/skins/skin{n}.png"),
    )


def make_catalog_item(texture: Texture, author_id: int = 1) -> TextureCatalogItem:
    return TextureCatalogItem(
        title=ContentLabel("Cool Skin"),
        texture=texture,
        author_id=author_id,
        published_at=datetime.now(UTC),
    )


@pytest.fixture
async def saved_texture(db_session):
    return await SqlTextureRepository(db_session).save(make_texture())


async def test_save_assigns_id(db_session, saved_user, saved_texture):
    repo = SqlTextureCatalogRepository(db_session)

    item = await repo.save(make_catalog_item(saved_texture, author_id=saved_user.id))

    assert item.id is not None
    assert item.texture.hash == saved_texture.hash


async def test_get_by_id_found(db_session, saved_user, saved_texture):
    repo = SqlTextureCatalogRepository(db_session)
    item = await repo.save(make_catalog_item(saved_texture, author_id=saved_user.id))

    found = await repo.get_by_id(id=item.id)

    assert found is not None
    assert found.id == item.id
    assert found.texture.hash == saved_texture.hash


async def test_get_by_id_not_found(db_session):
    repo = SqlTextureCatalogRepository(db_session)

    found = await repo.get_by_id(id=999_999)

    assert found is None


async def test_get_by_id_or_raise_not_found(db_session):
    from domain.exceptions.wardrobe import TextureCatalogItemNotFoundError
    repo = SqlTextureCatalogRepository(db_session)

    with pytest.raises(TextureCatalogItemNotFoundError):
        await repo.get_by_id_or_raise(id=999_999)


async def test_get_all_returns_empty(db_session):
    repo = SqlTextureCatalogRepository(db_session)

    result = await repo.get_all()

    assert result == []


async def test_get_all_returns_all_items(db_session, saved_user):
    texture1 = await SqlTextureRepository(db_session).save(make_texture(1))
    texture2 = await SqlTextureRepository(db_session).save(make_texture(2))
    repo = SqlTextureCatalogRepository(db_session)
    await repo.save(make_catalog_item(texture1, author_id=saved_user.id))
    await repo.save(make_catalog_item(texture2, author_id=saved_user.id))

    result = await repo.get_all()

    assert len(result) == 2
    assert {item.texture.hash for item in result} == {texture1.hash, texture2.hash}


async def test_get_all_loads_texture(db_session, saved_user, saved_texture):
    repo = SqlTextureCatalogRepository(db_session)
    await repo.save(make_catalog_item(saved_texture, author_id=saved_user.id))

    result = await repo.get_all()

    assert result[0].texture.url == saved_texture.url


async def test_delete_removes_item(db_session, saved_user, saved_texture):
    repo = SqlTextureCatalogRepository(db_session)
    item = await repo.save(make_catalog_item(saved_texture, author_id=saved_user.id))

    await repo.delete(item=item)

    assert await repo.get_by_id(id=item.id) is None

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from application.use_cases.wardrobe.catalog.add_texture_from_catalog import (
    AddTextureFromCatalogRequest,
    AddTextureFromCatalogUseCase,
)
from application.use_cases.wardrobe.catalog.edit_texture_catalog_item import (
    EditTextureCatalogItemRequest,
    EditTextureCatalogItemUseCase,
)
from application.use_cases.wardrobe.catalog.publish_texture import PublishTextureRequest, PublishTextureUseCase
from application.use_cases.wardrobe.catalog.unpublish_texture import UnpublishTextureRequest, UnpublishTextureUseCase
from application.use_cases.wardrobe.change_player_cosmetics import (
    ChangePlayerCosmeticsRequest,
    ChangePlayerCosmeticsUseCase,
)
from application.use_cases.wardrobe.edit_wardrobe_item import EditWardrobeItemRequest, EditWardrobeItemUseCase
from application.use_cases.wardrobe.remove_wardrobe_item import RemoveWardrobeItemRequest, RemoveWardrobeItemUseCase
from application.use_cases.wardrobe.upload_texture import UploadTextureRequest, UploadTextureUseCase
from domain.entities.base import ContentLabel, Url
from domain.entities.user import User
from domain.entities.wardrobe import Texture, TextureCatalogItem, TextureType, WardrobeItem
from domain.exceptions.auth import AccessDeniedError
from domain.exceptions.wardrobe import CannotPublishAddedTextureError
from domain.interfaces.services.file_storage import FileStorage
from domain.interfaces.services.texture_service import TextureService
from domain.interfaces.unit_of_work import UnitOfWork


def _skin_texture():
    return Texture(hash="ab" * 32, type=TextureType.SKIN, url=Url("https://example.com/skins/a.png"))


def _cape_texture():
    return Texture(hash="cd" * 32, type=TextureType.CAPE, url=Url("https://example.com/capes/b.png"))


def _wardrobe_item(user_id: int = 1, author_id: int = 1, texture=None):
    return WardrobeItem(
        id=11,
        user_id=user_id,
        author_id=author_id,
        texture=texture or _skin_texture(),
        acquired_at=datetime.now(UTC),
        label=ContentLabel("My texture"),
    )


def _catalog_item(author_id: int = 1):
    return TextureCatalogItem(
        id=5,
        title=ContentLabel("Catalog skin"),
        texture=_skin_texture(),
        author_id=author_id,
        published_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_upload_texture_saves_new_texture_and_item(mock_uow: UnitOfWork, active_user: User, mocker):
    file_storage = mocker.MagicMock(spec=FileStorage)
    texture_service = mocker.MagicMock(spec=TextureService)
    file_storage.upload_file.side_effect = [
        Url("https://example.com/skins/new.png"),
        Url("https://example.com/avatars/new.png"),
    ]

    mock_uow.textures.get_texture_by_hash = AsyncMock(return_value=None)
    mock_uow.textures.save = AsyncMock(return_value=_skin_texture())
    mock_uow.wardrobe.save = AsyncMock(return_value=_wardrobe_item())
    texture_service.generate_3d_head_from_skin.return_value = b"avatar"

    uc = UploadTextureUseCase(uow=mock_uow, file_storage=file_storage, texture_service=texture_service)
    result = await uc.execute(
        dto=UploadTextureRequest(file_bytes=b"png-bytes", label=ContentLabel("Skin one"), type=TextureType.SKIN),
        user=active_user,
    )

    assert result.texture.type == "skin"
    texture_service.validate_texture.assert_called_once()
    mock_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_edit_wardrobe_item_updates_label(mock_uow: UnitOfWork, active_user: User):
    item = _wardrobe_item()
    mock_uow.wardrobe.get_by_id_from_user_wardrobe_or_raise = AsyncMock(return_value=item)
    mock_uow.wardrobe.save = AsyncMock(return_value=item)

    uc = EditWardrobeItemUseCase(uow=mock_uow)
    await uc.execute(dto=EditWardrobeItemRequest(id=11, label=ContentLabel("New label")), user=active_user)

    assert item.label.value == "New label"
    mock_uow.wardrobe.save.assert_awaited_once_with(item=item)


@pytest.mark.asyncio
async def test_remove_wardrobe_item_calls_delete(mock_uow: UnitOfWork, active_user: User):
    item = _wardrobe_item()
    mock_uow.wardrobe.get_by_id_from_user_wardrobe_or_raise = AsyncMock(return_value=item)
    uc = RemoveWardrobeItemUseCase(uow=mock_uow)

    result = await uc.execute(dto=RemoveWardrobeItemRequest(id=11), user=active_user)

    assert result.ok is True
    mock_uow.wardrobe.delete.assert_awaited_once_with(item=item)


@pytest.mark.asyncio
async def test_change_player_cosmetics_updates_active_skin(mock_uow: UnitOfWork, active_user: User):
    item = _wardrobe_item()
    mc_profile = SimpleNamespace(active_skin_id=None, active_cape_id=None)
    mock_uow.wardrobe.get_by_id_from_user_wardrobe_or_raise = AsyncMock(return_value=item)
    mock_uow.minecraft_profiles.get_by_user_id_or_raise = AsyncMock(return_value=mc_profile)
    uc = ChangePlayerCosmeticsUseCase(uow=mock_uow)

    await uc.execute(dto=ChangePlayerCosmeticsRequest(item_id=item.id), user=active_user)

    assert mc_profile.active_skin_id == item.id
    mock_uow.minecraft_profiles.save.assert_awaited_once_with(profile=mc_profile)


@pytest.mark.asyncio
async def test_publish_texture_fails_for_catalog_added_texture(mock_uow: UnitOfWork, active_user: User):
    item = _wardrobe_item(user_id=active_user.id, author_id=999)
    mock_uow.wardrobe.get_by_id_from_user_wardrobe_or_raise = AsyncMock(return_value=item)
    uc = PublishTextureUseCase(uow=mock_uow)

    with pytest.raises(CannotPublishAddedTextureError):
        await uc.execute(
            dto=PublishTextureRequest(wardrobe_item_id=item.id, title=ContentLabel("Public skin")),
            user=active_user,
        )

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_unpublish_texture_fails_for_non_author(mock_uow: UnitOfWork, active_user: User):
    catalog_item = TextureCatalogItem(
        id=5,
        title=ContentLabel("Catalog"),
        texture=_skin_texture(),
        author_id=777,
        published_at=datetime.now(UTC),
    )
    mock_uow.texture_catalog.get_by_id_or_raise = AsyncMock(return_value=catalog_item)
    uc = UnpublishTextureUseCase(uow=mock_uow)

    with pytest.raises(AccessDeniedError):
        await uc.execute(dto=UnpublishTextureRequest(id=5), user=active_user)

    mock_uow.texture_catalog.delete.assert_not_called()


@pytest.mark.asyncio
async def test_add_texture_from_catalog_creates_user_item(mock_uow: UnitOfWork, active_user: User):
    catalog_item = TextureCatalogItem(
        id=5,
        title=ContentLabel("Catalog skin"),
        texture=_skin_texture(),
        author_id=700,
        published_at=datetime.now(UTC),
    )
    saved = _wardrobe_item(user_id=active_user.id, author_id=700)
    mock_uow.texture_catalog.get_by_id_or_raise = AsyncMock(return_value=catalog_item)
    mock_uow.wardrobe.save = AsyncMock(return_value=saved)
    uc = AddTextureFromCatalogUseCase(uow=mock_uow)

    result = await uc.execute(dto=AddTextureFromCatalogRequest(id=5), user=active_user)

    assert result.author_id == 700
    assert result.user_id == active_user.id


@pytest.mark.asyncio
async def test_upload_texture_reuses_existing_texture(mock_uow: UnitOfWork, active_user: User, mocker):
    existing_texture = _skin_texture()
    file_storage = mocker.MagicMock(spec=FileStorage)
    texture_service = mocker.MagicMock(spec=TextureService)
    mock_uow.textures.get_texture_by_hash = AsyncMock(return_value=existing_texture)
    mock_uow.wardrobe.save = AsyncMock(return_value=_wardrobe_item())

    uc = UploadTextureUseCase(uow=mock_uow, file_storage=file_storage, texture_service=texture_service)
    result = await uc.execute(
        dto=UploadTextureRequest(file_bytes=b"png-bytes", label=ContentLabel("Skin one"), type=TextureType.SKIN),
        user=active_user,
    )

    file_storage.upload_file.assert_not_called()
    mock_uow.wardrobe.save.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    assert result.texture.type == "skin"


@pytest.mark.asyncio
async def test_change_player_cosmetics_updates_active_cape(mock_uow: UnitOfWork, active_user: User):
    item = _wardrobe_item(texture=_cape_texture())
    item.id = 12
    mc_profile = SimpleNamespace(active_skin_id=None, active_cape_id=None)
    mock_uow.wardrobe.get_by_id_from_user_wardrobe_or_raise = AsyncMock(return_value=item)
    mock_uow.minecraft_profiles.get_by_user_id_or_raise = AsyncMock(return_value=mc_profile)
    uc = ChangePlayerCosmeticsUseCase(uow=mock_uow)

    await uc.execute(dto=ChangePlayerCosmeticsRequest(item_id=item.id), user=active_user)

    assert mc_profile.active_cape_id == item.id
    assert mc_profile.active_skin_id is None
    mock_uow.minecraft_profiles.save.assert_awaited_once_with(profile=mc_profile)


@pytest.mark.asyncio
async def test_publish_texture_success(mock_uow: UnitOfWork, active_user: User):
    item = _wardrobe_item(user_id=active_user.id, author_id=active_user.id)
    published = _catalog_item(author_id=active_user.id)
    mock_uow.wardrobe.get_by_id_from_user_wardrobe_or_raise = AsyncMock(return_value=item)
    mock_uow.texture_catalog.save = AsyncMock(return_value=published)
    uc = PublishTextureUseCase(uow=mock_uow)

    result = await uc.execute(
        dto=PublishTextureRequest(wardrobe_item_id=item.id, title=ContentLabel("Catalog skin")),
        user=active_user,
    )

    assert result.author_id == active_user.id
    mock_uow.texture_catalog.save.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_unpublish_texture_success(mock_uow: UnitOfWork, active_user: User):
    item = _catalog_item(author_id=active_user.id)
    mock_uow.texture_catalog.get_by_id_or_raise = AsyncMock(return_value=item)
    uc = UnpublishTextureUseCase(uow=mock_uow)

    result = await uc.execute(dto=UnpublishTextureRequest(id=item.id), user=active_user)

    assert result.ok is True
    mock_uow.texture_catalog.delete.assert_awaited_once_with(item=item)
    mock_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_edit_texture_catalog_item_fails_for_non_author(mock_uow: UnitOfWork, active_user: User):
    item = _catalog_item(author_id=999)
    mock_uow.texture_catalog.get_by_id_or_raise = AsyncMock(return_value=item)
    uc = EditTextureCatalogItemUseCase(uow=mock_uow)

    with pytest.raises(AccessDeniedError):
        await uc.execute(dto=EditTextureCatalogItemRequest(id=item.id, title=ContentLabel("New title")), user=active_user)

    mock_uow.texture_catalog.save.assert_not_called()


@pytest.mark.asyncio
async def test_edit_texture_catalog_item_success(mock_uow: UnitOfWork, active_user: User):
    item = _catalog_item(author_id=active_user.id)
    updated = _catalog_item(author_id=active_user.id)
    mock_uow.texture_catalog.get_by_id_or_raise = AsyncMock(return_value=item)
    mock_uow.texture_catalog.save = AsyncMock(return_value=updated)
    uc = EditTextureCatalogItemUseCase(uow=mock_uow)

    result = await uc.execute(
        dto=EditTextureCatalogItemRequest(id=item.id, title=ContentLabel("New title")),
        user=active_user,
    )

    assert result.author_id == active_user.id
    mock_uow.texture_catalog.save.assert_awaited_once_with(item=item)
    mock_uow.commit.assert_awaited_once()

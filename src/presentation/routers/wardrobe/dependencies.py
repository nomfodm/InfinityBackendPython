from typing import Annotated

from fastapi import Depends

from application.use_cases.wardrobe.catalog.add_texture_from_catalog import AddTextureFromCatalogUseCase
from application.use_cases.wardrobe.catalog.edit_texture_catalog_item import EditTextureCatalogItemUseCase
from application.use_cases.wardrobe.catalog.get_texture_catalog import GetTextureCatalogUseCase
from application.use_cases.wardrobe.catalog.publish_texture import PublishTextureUseCase
from application.use_cases.wardrobe.catalog.unpublish_texture import UnpublishTextureUseCase
from application.use_cases.wardrobe.change_player_cosmetics import ChangePlayerCosmeticsUseCase
from application.use_cases.wardrobe.edit_wardrobe_item import EditWardrobeItemUseCase
from application.use_cases.wardrobe.remove_wardrobe_item import RemoveWardrobeItemUseCase
from application.use_cases.wardrobe.upload_texture import UploadTextureUseCase
from domain.interfaces.services.file_storage import FileStorage
from domain.interfaces.services.texture_service import TextureService
from domain.interfaces.unit_of_work import UnitOfWork
from presentation.dependencies.services import get_file_storage, get_texture_service
from presentation.dependencies.uow import get_uow

UOW = Annotated[UnitOfWork, Depends(get_uow)]
FILE_STORAGE = Annotated[FileStorage, Depends(get_file_storage)]
TEXTURE_SERVICE = Annotated[TextureService, Depends(get_texture_service)]


def get_upload_texture_uc(
    uow: UOW,
    file_storage: FILE_STORAGE,
    texture_service: TEXTURE_SERVICE,
) -> UploadTextureUseCase:
    return UploadTextureUseCase(uow=uow, file_storage=file_storage, texture_service=texture_service)


def get_add_from_catalog_uc(uow: UOW) -> AddTextureFromCatalogUseCase:
    return AddTextureFromCatalogUseCase(uow=uow)


def get_edit_wardrobe_item_uc(uow: UOW) -> EditWardrobeItemUseCase:
    return EditWardrobeItemUseCase(uow=uow)


def get_remove_wardrobe_item_uc(uow: UOW) -> RemoveWardrobeItemUseCase:
    return RemoveWardrobeItemUseCase(uow=uow)


def get_change_cosmetics_uc(uow: UOW) -> ChangePlayerCosmeticsUseCase:
    return ChangePlayerCosmeticsUseCase(uow=uow)


def get_texture_catalog_uc(uow: UOW) -> GetTextureCatalogUseCase:
    return GetTextureCatalogUseCase(uow=uow)


def get_publish_texture_uc(uow: UOW) -> PublishTextureUseCase:
    return PublishTextureUseCase(uow=uow)


def get_unpublish_texture_uc(uow: UOW) -> UnpublishTextureUseCase:
    return UnpublishTextureUseCase(uow=uow)


def get_edit_catalog_item_uc(uow: UOW) -> EditTextureCatalogItemUseCase:
    return EditTextureCatalogItemUseCase(uow=uow)

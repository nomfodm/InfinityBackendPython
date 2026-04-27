from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile

from application.dtos.common import StatusResponse
from application.dtos.wardrobe import TextureCatalogItemResponse, WardrobeItemResponse
from application.use_cases.wardrobe.catalog.add_texture_from_catalog import (
    AddTextureFromCatalogRequest,
    AddTextureFromCatalogUseCase,
)
from application.use_cases.wardrobe.catalog.edit_texture_catalog_item import (
    EditTextureCatalogItemRequest,
    EditTextureCatalogItemUseCase,
)
from application.use_cases.wardrobe.catalog.get_texture_catalog import GetTextureCatalogUseCase
from application.use_cases.wardrobe.catalog.publish_texture import PublishTextureRequest, PublishTextureUseCase
from application.use_cases.wardrobe.catalog.unpublish_texture import UnpublishTextureRequest, UnpublishTextureUseCase
from application.use_cases.wardrobe.change_player_cosmetics import (
    ChangePlayerCosmeticsRequest,
    ChangePlayerCosmeticsUseCase,
)
from application.use_cases.wardrobe.edit_wardrobe_item import EditWardrobeItemRequest, EditWardrobeItemUseCase
from application.use_cases.wardrobe.remove_wardrobe_item import RemoveWardrobeItemRequest, RemoveWardrobeItemUseCase
from application.use_cases.wardrobe.upload_texture import UploadTextureRequest, UploadTextureUseCase
from domain.entities.base import ContentLabel
from domain.entities.wardrobe import TextureType
from presentation.dependencies.auth import CURRENT_USER
from presentation.routers.wardrobe.dependencies import (
    get_add_from_catalog_uc,
    get_change_cosmetics_uc,
    get_edit_catalog_item_uc,
    get_edit_wardrobe_item_uc,
    get_publish_texture_uc,
    get_remove_wardrobe_item_uc,
    get_texture_catalog_uc,
    get_unpublish_texture_uc,
    get_upload_texture_uc,
)
from presentation.routers.wardrobe.schemas import (
    ChangePlayerCosmeticsRequest as ChangePlayerCosmeticsSchema,
)
from presentation.routers.wardrobe.schemas import (
    EditCatalogItemRequest,
)
from presentation.routers.wardrobe.schemas import (
    EditWardrobeItemRequest as EditWardrobeItemSchema,
)
from presentation.routers.wardrobe.schemas import (
    PublishTextureRequest as PublishTextureSchema,
)

wardrobe_router = APIRouter(prefix="/wardrobe", tags=["wardrobe"])


@wardrobe_router.get("/catalog", response_model=list[TextureCatalogItemResponse])
async def get_catalog(
    uc: Annotated[GetTextureCatalogUseCase, Depends(get_texture_catalog_uc)],
):
    return await uc.execute()


@wardrobe_router.post("/items", response_model=WardrobeItemResponse, status_code=201)
async def upload_texture(
    file: UploadFile,
    label: Annotated[str, Form()],
    type: Annotated[TextureType, Form()],
    user: CURRENT_USER,
    uc: Annotated[UploadTextureUseCase, Depends(get_upload_texture_uc)],
):
    file_bytes = await file.read()
    return await uc.execute(
        dto=UploadTextureRequest(
            file_bytes=file_bytes,
            label=ContentLabel(label),
            type=type,
        ),
        user=user,
    )


@wardrobe_router.post("/items/from-catalog/{catalog_item_id}", response_model=WardrobeItemResponse, status_code=201)
async def add_from_catalog(
    catalog_item_id: int,
    user: CURRENT_USER,
    uc: Annotated[AddTextureFromCatalogUseCase, Depends(get_add_from_catalog_uc)],
):
    return await uc.execute(dto=AddTextureFromCatalogRequest(id=catalog_item_id), user=user)


@wardrobe_router.patch("/items/{item_id}", response_model=WardrobeItemResponse)
async def edit_wardrobe_item(
    item_id: int,
    data: EditWardrobeItemSchema,
    user: CURRENT_USER,
    uc: Annotated[EditWardrobeItemUseCase, Depends(get_edit_wardrobe_item_uc)],
):
    return await uc.execute(dto=EditWardrobeItemRequest(id=item_id, label=ContentLabel(data.label)), user=user)


@wardrobe_router.delete("/items/{item_id}", response_model=StatusResponse)
async def remove_wardrobe_item(
    item_id: int,
    user: CURRENT_USER,
    uc: Annotated[RemoveWardrobeItemUseCase, Depends(get_remove_wardrobe_item_uc)],
):
    return await uc.execute(dto=RemoveWardrobeItemRequest(id=item_id), user=user)


@wardrobe_router.patch("/cosmetics", response_model=StatusResponse)
async def change_cosmetics(
    data: ChangePlayerCosmeticsSchema,
    user: CURRENT_USER,
    uc: Annotated[ChangePlayerCosmeticsUseCase, Depends(get_change_cosmetics_uc)],
):
    return await uc.execute(dto=ChangePlayerCosmeticsRequest(item_id=data.item_id), user=user)


@wardrobe_router.post("/catalog/items", response_model=TextureCatalogItemResponse, status_code=201)
async def publish_texture(
    data: PublishTextureSchema,
    user: CURRENT_USER,
    uc: Annotated[PublishTextureUseCase, Depends(get_publish_texture_uc)],
):
    return await uc.execute(
        dto=PublishTextureRequest(
            wardrobe_item_id=data.wardrobe_item_id,
            title=ContentLabel(data.title),
        ),
        user=user,
    )


@wardrobe_router.patch("/catalog/{catalog_id}", response_model=TextureCatalogItemResponse)
async def edit_catalog_item(
    catalog_id: int,
    data: EditCatalogItemRequest,
    user: CURRENT_USER,
    uc: Annotated[EditTextureCatalogItemUseCase, Depends(get_edit_catalog_item_uc)],
):
    return await uc.execute(dto=EditTextureCatalogItemRequest(id=catalog_id, title=ContentLabel(data.title)), user=user)


@wardrobe_router.delete("/catalog/{catalog_id}", response_model=StatusResponse)
async def unpublish_texture(
    catalog_id: int,
    user: CURRENT_USER,
    uc: Annotated[UnpublishTextureUseCase, Depends(get_unpublish_texture_uc)],
):
    return await uc.execute(dto=UnpublishTextureRequest(id=catalog_id), user=user)

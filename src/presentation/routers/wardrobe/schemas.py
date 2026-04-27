from pydantic import BaseModel

from domain.entities.wardrobe import TextureType


class UploadTextureRequest(BaseModel):
    label: str
    type: TextureType


class AddFromCatalogRequest(BaseModel):
    id: int


class EditWardrobeItemRequest(BaseModel):
    label: str


class ChangePlayerCosmeticsRequest(BaseModel):
    item_id: int | None


class PublishTextureRequest(BaseModel):
    wardrobe_item_id: int
    title: str


class EditCatalogItemRequest(BaseModel):
    title: str

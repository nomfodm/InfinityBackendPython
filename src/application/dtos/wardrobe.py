from dataclasses import dataclass
from datetime import datetime

from domain.entities.wardrobe import TextureCatalogItem, WardrobeItem


@dataclass(frozen=True)
class TextureResponse:
    id: int | None
    hash: str
    type: str
    url: str
    model: str | None
    avatar_url: str | None

    @classmethod
    def from_domain(cls, texture):
        return cls(
            id=texture.id,
            hash=texture.hash,
            type=texture.type.value,
            url=texture.url.value,
            model=texture.model.value if texture.model else None,
            avatar_url=texture.avatar_url.value if texture.avatar_url else None,
        )


@dataclass(frozen=True)
class WardrobeItemResponse:
    id: int | None
    user_id: int
    author_id: int
    label: str
    acquired_at: datetime
    texture: TextureResponse

    @classmethod
    def from_domain(cls, item: WardrobeItem):
        return cls(
            id=item.id,
            user_id=item.user_id,
            author_id=item.author_id,
            label=item.label.value,
            acquired_at=item.acquired_at,
            texture=TextureResponse.from_domain(item.texture),
        )


@dataclass(frozen=True)
class TextureCatalogItemResponse:
    id: int | None
    title: str
    author_id: int
    published_at: datetime
    texture: TextureResponse

    @classmethod
    def from_domain(cls, item: TextureCatalogItem):
        return cls(
            id=item.id,
            title=item.title.value,
            author_id=item.author_id,
            published_at=item.published_at,
            texture=TextureResponse.from_domain(item.texture),
        )

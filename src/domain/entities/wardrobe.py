from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from domain.entities.base import ContentLabel, Url


class TextureType(str, Enum):
    SKIN = "skin"
    CAPE = "cape"


class SkinModel(str, Enum):
    CLASSIC = "classic"
    SLIM = "slim"


@dataclass
class Texture:
    hash: str  # Unique constraint
    type: TextureType
    url: Url

    id: int | None = None
    model: SkinModel | None = None

    @property
    def avatar_url(self) -> Url | None:
        if self.type != TextureType.SKIN:
            return None
        return Url(self.url.value.replace("/skins/", "/avatars/"))


@dataclass
class TextureCatalogItem:
    title: ContentLabel
    texture: Texture
    author_id: int
    published_at: datetime

    id: int | None = None


@dataclass
class WardrobeItem:
    user_id: int
    author_id: int
    texture: Texture
    acquired_at: datetime
    label: ContentLabel

    id: int | None = None


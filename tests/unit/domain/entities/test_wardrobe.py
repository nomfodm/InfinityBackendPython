from domain.entities.base import Url
from domain.entities.wardrobe import Texture, TextureType


def test_texture_avatar_url_for_skin():
    texture = Texture(hash="ab" * 32, type=TextureType.SKIN, url=Url("https://cdn.test/skins/file.png"))
    assert texture.avatar_url is not None
    assert "/avatars/" in texture.avatar_url.value


def test_texture_avatar_url_for_cape_is_none():
    texture = Texture(hash="ab" * 32, type=TextureType.CAPE, url=Url("https://cdn.test/capes/file.png"))
    assert texture.avatar_url is None

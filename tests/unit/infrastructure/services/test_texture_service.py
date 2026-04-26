from io import BytesIO

import pytest
from PIL import Image

from domain.entities.wardrobe import TextureType
from domain.exceptions.base import ValidationError
from infrastructure.services.texture_service import PillowTextureService


def make_png(width: int, height: int) -> bytes:
    buf = BytesIO()
    Image.new("RGBA", (width, height), (255, 0, 0, 128)).save(buf, format="PNG")
    return buf.getvalue()


def make_jpeg(width: int, height: int) -> bytes:
    buf = BytesIO()
    Image.new("RGB", (width, height)).save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def service():
    return PillowTextureService()


@pytest.fixture
def skin_64x64():
    return make_png(64, 64)


@pytest.fixture
def cape_64x32():
    return make_png(64, 32)


class TestValidateTexture:
    def test_valid_skin_64x64(self, service, skin_64x64):
        service.validate_texture(file_bytes=skin_64x64, texture_type=TextureType.SKIN)

    def test_valid_cape_64x32(self, service, cape_64x32):
        service.validate_texture(file_bytes=cape_64x32, texture_type=TextureType.CAPE)

    def test_skin_wrong_size_raises(self, service):
        wrong = make_png(128, 128)

        with pytest.raises(ValidationError):
            service.validate_texture(file_bytes=wrong, texture_type=TextureType.SKIN)

    def test_cape_wrong_size_raises(self, service):
        wrong = make_png(64, 64)

        with pytest.raises(ValidationError):
            service.validate_texture(file_bytes=wrong, texture_type=TextureType.CAPE)

    def test_non_png_raises(self, service):
        jpeg = make_jpeg(64, 64)

        with pytest.raises(ValidationError):
            service.validate_texture(file_bytes=jpeg, texture_type=TextureType.SKIN)

    def test_garbage_bytes_raises(self, service):
        with pytest.raises(ValidationError):
            service.validate_texture(file_bytes=b"not an image at all", texture_type=TextureType.SKIN)


class TestGenerate3dHead:
    def test_returns_png_bytes(self, service, skin_64x64):
        result = service.generate_3d_head_from_skin(skin_bytes=skin_64x64)

        img = Image.open(BytesIO(result))
        assert img.format == "PNG"

    def test_default_size_128(self, service, skin_64x64):
        result = service.generate_3d_head_from_skin(skin_bytes=skin_64x64)

        img = Image.open(BytesIO(result))
        assert img.size == (128, 128)

    def test_custom_size(self, service, skin_64x64):
        result = service.generate_3d_head_from_skin(skin_bytes=skin_64x64, size=64)

        img = Image.open(BytesIO(result))
        assert img.size == (64, 64)

    def test_output_is_rgba(self, service, skin_64x64):
        result = service.generate_3d_head_from_skin(skin_bytes=skin_64x64)

        img = Image.open(BytesIO(result))
        assert img.mode == "RGBA"

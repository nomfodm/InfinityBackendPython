from io import BytesIO

from PIL import Image, UnidentifiedImageError

from domain.entities.wardrobe import TextureType
from domain.exceptions.base import ValidationError
from domain.interfaces.services.texture_service import TextureService

_VALID_SIZES: dict[TextureType, set[tuple[int, int]]] = {
    TextureType.SKIN: {(64, 64)},
    TextureType.CAPE: {(64, 32)},
}


class PillowTextureService(TextureService):
    def validate_texture(self, file_bytes: bytes, texture_type: TextureType) -> None:
        try:
            img = Image.open(BytesIO(file_bytes))
            img.verify()
        except UnidentifiedImageError:
            raise ValidationError("Файл не является изображением.") from None
        except Exception:
            raise ValidationError("Повреждённый файл изображения.") from None

        img = Image.open(BytesIO(file_bytes))

        if img.format != "PNG":
            raise ValidationError("Текстура должна быть в формате PNG.")

        valid_sizes = _VALID_SIZES[texture_type]
        if img.size not in valid_sizes:
            sizes_str = " или ".join(f"{w}x{h}" for w, h in sorted(valid_sizes))
            raise ValidationError(f"Неверный размер текстуры. Допустимо: {sizes_str}.")

    def generate_3d_head_from_skin(self, skin_bytes: bytes, size: int = 128) -> bytes:
        skin = Image.open(BytesIO(skin_bytes)).convert("RGBA")

        face = skin.crop((8, 8, 16, 16)).resize((size, size), Image.NEAREST)
        hat = skin.crop((40, 8, 48, 16)).resize((size, size), Image.NEAREST)

        # apply hat overlay using its alpha channel as mask
        face.paste(hat, (0, 0), hat)

        output = BytesIO()
        face.save(output, format="PNG")
        return output.getvalue()

from io import BytesIO

from PIL import Image, UnidentifiedImageError

from domain.entities.wardrobe import SkinModel, TextureType
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

    def detect_skin_model(self, skin_bytes: bytes) -> SkinModel:
        img = Image.open(BytesIO(skin_bytes)).convert("RGBA")
        if img.height < 64:
            return SkinModel.CLASSIC
        _, _, _, alpha = img.getpixel((46, 52))
        return SkinModel.SLIM if alpha == 0 else SkinModel.CLASSIC

    def generate_3d_head_from_skin(self, skin_bytes: bytes, size: int = 128) -> bytes:
        skin = Image.open(BytesIO(skin_bytes)).convert("RGBA")

        S = size // 2
        h = S / 2

        def get_face(box: tuple[int, int, int, int]) -> Image.Image:
            return skin.crop(box).resize((S, S), Image.NEAREST)

        top = get_face((8, 0, 16, 8))
        left = get_face((0, 8, 8, 16))
        front = get_face((8, 8, 16, 16))

        if skin.height == 64:
            for face_img, hat_box in (
                (top, (40, 0, 48, 8)),
                (left, (32, 8, 40, 16)),
                (front, (40, 8, 48, 16)),
            ):
                hat = get_face(hat_box)
                face_img.paste(hat, (0, 0), hat)

        canvas = Image.new("RGBA", (2 * S, 2 * S), (0, 0, 0, 0))
        side_h = round(1.5 * S)

        top_t = top.transform(
            (2 * S, S),
            Image.AFFINE,
            (0.5, 1.0, -h, -0.5, 1.0, h),
            Image.NEAREST,
            fillcolor=(0, 0, 0, 0),
        )
        left_t = left.transform(
            (S, side_h),
            Image.AFFINE,
            (1.0, 0.0, 0.0, -0.5, 1.0, 0.0),
            Image.NEAREST,
            fillcolor=(0, 0, 0, 0),
        )
        front_t = front.transform(
            (S, side_h),
            Image.AFFINE,
            (1.0, 0.0, 0.0, 0.5, 1.0, -h),
            Image.NEAREST,
            fillcolor=(0, 0, 0, 0),
        )

        def composite(dst: Image.Image, src: Image.Image, pos: tuple[int, int]) -> Image.Image:
            tmp = Image.new("RGBA", dst.size, (0, 0, 0, 0))
            tmp.paste(src, pos)
            return Image.alpha_composite(dst, tmp)

        canvas = composite(canvas, top_t, (0, 0))
        canvas = composite(canvas, left_t, (0, S // 2))
        canvas = composite(canvas, front_t, (S, S // 2))

        output = BytesIO()
        canvas.save(output, format="PNG")
        return output.getvalue()

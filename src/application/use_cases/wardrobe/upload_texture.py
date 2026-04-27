import datetime
from dataclasses import dataclass
from datetime import UTC

from application.decorators.auth import require_login, require_not_banned
from application.dtos.wardrobe import WardrobeItemResponse
from domain.entities.base import ContentLabel
from domain.entities.user import User
from domain.entities.wardrobe import SkinModel, Texture, TextureType, WardrobeItem
from domain.interfaces.services.file_storage import FileStorage
from domain.interfaces.services.texture_service import TextureService
from domain.interfaces.unit_of_work import UnitOfWork
from domain.utils.crypto import sha256
from domain.utils.storage_path import get_avatar_path, get_texture_path


@dataclass(frozen=True)
class UploadTextureRequest:
    file_bytes: bytes
    label: ContentLabel
    type: TextureType


class UploadTextureUseCase:
    def __init__(self, *, uow: UnitOfWork, file_storage: FileStorage, texture_service: TextureService):
        self._uow = uow
        self._file_storage = file_storage
        self._texture_service = texture_service

    @require_login
    @require_not_banned
    async def execute(self, *, dto: UploadTextureRequest, user: User) -> WardrobeItemResponse:
        self._texture_service.validate_texture(file_bytes=dto.file_bytes, texture_type=dto.type)

        texture_hash = sha256(dto.file_bytes)

        async with self._uow:
            texture = await self._uow.textures.get_texture_by_hash(hash_sha256=texture_hash)

            if texture is None:
                url = await self._file_storage.upload_file(
                    file_bytes=dto.file_bytes,
                    content_type="image/png",
                    destination_path=get_texture_path(texture_hash, dto.type),
                )

                model: SkinModel | None = None
                if dto.type == TextureType.SKIN:
                    model = self._texture_service.detect_skin_model(skin_bytes=dto.file_bytes)

                texture = await self._uow.textures.save(
                    texture=Texture(hash=texture_hash, type=dto.type, url=url, model=model)
                )

                if dto.type == TextureType.SKIN:
                    head_3d = self._texture_service.generate_3d_head_from_skin(skin_bytes=dto.file_bytes)
                    await self._file_storage.upload_file(
                        file_bytes=head_3d,
                        destination_path=get_avatar_path(file_hash=texture_hash),
                        content_type="image/png",
                    )

            wardrobe_item = await self._uow.wardrobe.save(
                item=WardrobeItem(
                    user_id=user.id,
                    author_id=user.id,
                    texture=texture,
                    label=dto.label,
                    acquired_at=datetime.datetime.now(UTC),
                )
            )

            await self._uow.commit()

            return WardrobeItemResponse.from_domain(wardrobe_item)

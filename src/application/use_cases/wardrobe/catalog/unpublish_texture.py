from dataclasses import dataclass

from application.decorators.auth import require_login
from application.dtos.common import StatusResponse
from domain.entities.user import User
from domain.exceptions.auth import AccessDeniedError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass
class UnpublishTextureRequest:
    id: int


class UnpublishTextureUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    async def execute(self, *, dto: UnpublishTextureRequest, user: User) -> StatusResponse:
        async with self._uow:
            item = await self._uow.texture_catalog.get_by_id_or_raise(id=dto.id)
            if item.author_id != user.id:
                raise AccessDeniedError("Эта текстура опубликована другим пользователем.")
            await self._uow.texture_catalog.delete(item=item)

            await self._uow.commit()
            return StatusResponse()


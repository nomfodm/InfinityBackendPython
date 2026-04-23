from dataclasses import dataclass

from application.decorators.auth import require_login
from application.dtos.common import StatusResponse
from domain.entities.user import User
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass
class RemoveWardrobeItemRequest:
    id: int


class RemoveWardrobeItemUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    async def execute(self, *, dto: RemoveWardrobeItemRequest, user: User) -> StatusResponse:
        async with self._uow:
            item = await self._uow.wardrobe.get_by_id_from_user_wardrobe_or_raise(id=dto.id, user_id=user.id)
            await self._uow.wardrobe.delete(item=item)
            await self._uow.commit()
            return StatusResponse()

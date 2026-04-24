from dataclasses import dataclass

from application.decorators.auth import require_login, require_not_banned
from application.dtos.wardrobe import WardrobeItemResponse
from domain.entities.base import ContentLabel
from domain.entities.user import User
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass
class EditWardrobeItemRequest:
    id: int
    label: ContentLabel


class EditWardrobeItemUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @require_not_banned
    async def execute(self, *, dto: EditWardrobeItemRequest, user: User) -> WardrobeItemResponse:
        async with self._uow:
            item = await self._uow.wardrobe.get_by_id_from_user_wardrobe_or_raise(id=dto.id, user_id=user.id)

            item.label = dto.label
            edited = await self._uow.wardrobe.save(item=item)

            await self._uow.commit()
            return WardrobeItemResponse.from_domain(edited)

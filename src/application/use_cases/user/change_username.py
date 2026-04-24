from dataclasses import dataclass

from application.decorators.auth import require_login, require_not_banned
from application.dtos.common import StatusResponse
from domain.entities.base import UserRelatedHandle
from domain.entities.user import User
from domain.exceptions.auth import UsernameTakenError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ChangeUsernameRequest:
    new_username: UserRelatedHandle


class ChangeUsernameUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @require_not_banned
    async def execute(self, *, dto: ChangeUsernameRequest, user: User) -> StatusResponse:
        async with self._uow:
            existing_username = await self._uow.users.get_by_username(username=dto.new_username)
            if existing_username and existing_username.id != user.id:
                raise UsernameTakenError("Это имя пользователя занято.")

            user.username = dto.new_username

            await self._uow.users.save(user=user)
            await self._uow.commit()
            return StatusResponse()

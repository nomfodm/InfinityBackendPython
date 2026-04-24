from dataclasses import dataclass

from application.decorators.auth import require_login, roles_allowed
from application.dtos.common import StatusResponse
from domain.entities.user import Role, User
from domain.exceptions.user import UserNotFoundError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class PardonUserRequest:
    user_to_pardon_id: int


class PardonUserUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @roles_allowed(Role.ADMIN)
    async def execute(self, *, dto: PardonUserRequest, user: User) -> StatusResponse:
        async with self._uow:
            user_to_pardon = await self._uow.users.get_by_id(id=dto.user_to_pardon_id)
            if user_to_pardon is None:
                raise UserNotFoundError("Пользователь не найден.")

            user_to_pardon.ban_status.banned_till = None
            user_to_pardon.ban_status.admin_user_id = None
            user_to_pardon.ban_status.is_banned = False
            user_to_pardon.ban_status.is_permanent = False

            user_to_pardon.ban_status.admin_user_id = user.id

            await self._uow.users.save(user=user_to_pardon)

            await self._uow.commit()
            return StatusResponse()

from dataclasses import dataclass

from application.decorators.auth import require_login, require_not_banned, roles_allowed
from application.dtos.common import StatusResponse
from domain.entities.user import Role, User
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ForceLogoutUserRequest:
    user_id: int


class ForceLogoutUserUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @require_not_banned
    @roles_allowed(Role.ADMIN)
    async def execute(self, *, dto: ForceLogoutUserRequest, user: User) -> StatusResponse:
        async with self._uow:
            await self._uow.sessions.delete_all_by_user_id(user_id=dto.user_id)

            await self._uow.commit()
            return StatusResponse()

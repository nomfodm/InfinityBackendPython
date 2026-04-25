from dataclasses import dataclass

from application.decorators.auth import require_login, require_not_banned, roles_allowed
from application.dtos.login_history import LoginHistoryEntryResponse
from domain.entities.user import Role, User
from domain.exceptions.user import UserNotFoundError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class GetUserLoginHistoryRequest:
    user_id: int


class GetUserLoginHistoryUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @require_not_banned
    @roles_allowed(Role.ADMIN)
    async def execute(self, *, dto: GetUserLoginHistoryRequest, user: User) -> list[LoginHistoryEntryResponse]:
        async with self._uow:
            existing_user = await self._uow.users.get_by_id(id=dto.user_id)
            if existing_user is None:
                raise UserNotFoundError("Пользователь не найден.")

            login_history = await self._uow.login_histories.get_by_user_id(user_id=dto.user_id)

            return [LoginHistoryEntryResponse.from_domain(entry) for entry in login_history]

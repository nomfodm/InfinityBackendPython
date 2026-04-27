from application.decorators.auth import require_login, require_not_banned
from application.dtos.login_history import LoginHistoryEntryResponse
from domain.entities.user import User
from domain.interfaces.unit_of_work import UnitOfWork


class GetLoginHistoryUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @require_not_banned
    async def execute(self, *, user: User) -> list[LoginHistoryEntryResponse]:
        async with self._uow:
            login_history = await self._uow.login_histories.get_by_user_id(user_id=user.id)

            return [LoginHistoryEntryResponse.from_domain(entry) for entry in login_history]

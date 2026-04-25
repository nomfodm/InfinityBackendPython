from application.dtos.auth import SessionCredentials
from application.dtos.login_history import LoginHistoryEntryResponse
from application.services.auth import AuthService
from domain.interfaces.unit_of_work import UnitOfWork


class GetLoginHistoryUseCase:
    def __init__(self, *, uow: UnitOfWork, auth_service: AuthService):
        self._uow = uow
        self._auth_service = auth_service

    async def execute(self, *, dto: SessionCredentials) -> list[LoginHistoryEntryResponse]:
        async with self._uow:
            session = await self._uow.sessions.get_by_id_or_raise(uuid=dto.id)
            self._auth_service.verify_session(refresh_token=dto.refresh_token, session=session)

            login_history = await self._uow.login_histories.get_by_user_id(user_id=session.user_id)

            return [LoginHistoryEntryResponse.from_domain(entry) for entry in login_history]

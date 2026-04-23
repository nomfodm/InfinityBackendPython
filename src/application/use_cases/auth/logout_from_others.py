from application.dtos.auth import SessionCredentials
from application.dtos.common import StatusResponse
from application.services.auth import AuthService
from domain.interfaces.unit_of_work import UnitOfWork


class LogoutFromOthersUseCase:
    def __init__(self, *, uow: UnitOfWork, auth_service: AuthService):
        self._uow = uow
        self._auth_service = auth_service

    async def execute(self, *, dto: SessionCredentials) -> StatusResponse:
        async with self._uow:
            session = await self._uow.sessions.get_by_id_or_raise(uuid=dto.id)
            self._auth_service.verify_session(refresh_token=dto.refresh_token, session=session)

            await self._uow.sessions.delete_others_by_user_id(user_id=session.user_id, exclude_session_id=session.id)

            await self._uow.commit()
            return StatusResponse()





from dataclasses import dataclass

from application.dtos.auth import SessionCredentials
from application.dtos.common import StatusResponse
from application.services.auth import AuthService
from domain.exceptions.auth import AccessDeniedError
from domain.exceptions.base import DomainError
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork

@dataclass(frozen=True)
class LogoutFromOthersRequest:
    password: str
    session_credentials: SessionCredentials


class LogoutFromOthersUseCase:
    def __init__(self, *, uow: UnitOfWork, hasher: StringHasher, auth_service: AuthService):
        self._uow = uow
        self._hasher = hasher
        self._auth_service = auth_service

    async def execute(self, *, dto: LogoutFromOthersRequest) -> StatusResponse:
        async with self._uow:
            session = await self._uow.sessions.get_by_id_or_raise(uuid=dto.session_credentials.id)
            self._auth_service.verify_session(refresh_token=dto.session_credentials.refresh_token, session=session)

            user = await self._uow.users.get_by_id(id=session.user_id)
            if user is None:
                raise DomainError("Что-то пошло не так...?")

            if not self._hasher.verify(raw=dto.password, hashed=user.password_hash):
                raise AccessDeniedError("Неверный пароль.")

            await self._uow.sessions.delete_others_by_user_id(user_id=session.user_id, exclude_session_id=session.id)

            await self._uow.commit()
            return StatusResponse()





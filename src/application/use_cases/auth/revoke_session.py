from dataclasses import dataclass
from uuid import UUID

from application.dtos.auth import SessionCredentials
from application.dtos.common import StatusResponse
from application.services.auth import AuthService
from domain.exceptions.session import CannotRevokeSessionError
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class RevokeSessionRequest:
    session_credentials: SessionCredentials
    session_id_to_revoke: UUID


class RevokeSessionUseCase:
    def __init__(self, *, uow: UnitOfWork, auth_service: AuthService):
        self._uow = uow
        self._auth_service = auth_service

    async def execute(self, *, dto: RevokeSessionRequest) -> StatusResponse:
        async with self._uow:
            session = await self._uow.sessions.get_by_id_or_raise(uuid=dto.session_credentials.id)
            self._auth_service.verify_session(refresh_token=dto.session_credentials.refresh_token, session=session)

            if session.id == dto.session_id_to_revoke:
                raise CannotRevokeSessionError("Нельзя отозвать свою же сессию.")

            session_to_revoke = await self._uow.sessions.get_by_id_or_raise(uuid=dto.session_id_to_revoke)
            if session.user_id != session_to_revoke.user_id:
                raise CannotRevokeSessionError("Нельзя отозвать чужую сессию.")

            session_to_revoke.is_revoked = True

            await self._uow.sessions.save(session=session_to_revoke)

            await self._uow.commit()
            return StatusResponse()

from application.dtos.auth import TokenPairResponse, SessionCredentials
from application.services.auth import AuthService
from domain.interfaces.unit_of_work import UnitOfWork


class RefreshSessionUseCase:
    def __init__(self, *, uow: UnitOfWork, auth_service: AuthService):
        self._uow = uow
        self._auth_service = auth_service

    async def execute(self, *, dto: SessionCredentials) -> TokenPairResponse:
        async with self._uow:
            session = await self._uow.sessions.get_by_id_or_raise(uuid=dto.id)
            self._auth_service.verify_session(refresh_token=dto.refresh_token, session=session)

            access_token = self._auth_service.generate_access_token(user_id=session.user_id)
            refresh_token, refresh_token_expires_at, refresh_token_hash = self._auth_service.generate_refresh_token()

            session.expires_at = refresh_token_expires_at
            session.refresh_token_hash = refresh_token_hash

            await self._uow.sessions.save(session=session)

            await self._uow.commit()

            return TokenPairResponse(
                access_token=access_token,
                refresh_split_token=f"{session.id}.{refresh_token}"
            )





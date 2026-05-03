import datetime
from dataclasses import dataclass
from datetime import UTC

from application.dtos.auth import TokenPairResponse
from application.services.auth import AuthService
from domain.entities.base import UserRelatedHandle
from domain.exceptions.auth import InvalidCredentialError
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class UserLoginRequest:
    username: UserRelatedHandle
    password: str
    user_agent: str | None
    ip_address: str | None


class LoginUseCase:
    def __init__(self, *, uow: UnitOfWork, hasher: StringHasher, auth_service: AuthService):
        self._uow = uow
        self._hasher = hasher
        self._auth_service = auth_service

    async def execute(self, *, dto: UserLoginRequest) -> TokenPairResponse:
        async with self._uow:
            user = await self._uow.users.get_by_username(username=dto.username)
            if user is None:
                raise InvalidCredentialError("Неверные логин или пароль.")

            if not self._hasher.verify(raw=dto.password, hashed=user.password_hash):
                raise InvalidCredentialError("Неверные логин или пароль.")

            await self._uow.sessions.delete_invalid_by_user_id(user_id=user.id)

            session_tokens = self._auth_service.create_session_and_tokens(user_id=user.id)

            session_tokens.session.user_agent = dto.user_agent
            session_tokens.session.ip_address = dto.ip_address
            session_tokens.session.last_used_at = datetime.datetime.now(UTC)

            await self._uow.sessions.save(session=session_tokens.session)

            await self._uow.commit()
            return session_tokens.tokens

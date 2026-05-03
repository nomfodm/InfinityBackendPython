import datetime
import uuid
from dataclasses import dataclass
from datetime import UTC

from application.dtos.auth import TokenPairResponse
from application.services.auth import AuthService
from domain.entities.base import Email, UserRelatedHandle
from domain.entities.minecraft_profile import MinecraftProfile
from domain.entities.user import User
from domain.exceptions.auth import EmailTakenError, UsernameTakenError
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class UserRegisterRequest:
    email: Email
    username: UserRelatedHandle
    password: str
    user_agent: str | None
    ip_address: str | None


class RegisterUserAndLoginUseCase:
    def __init__(self, *, uow: UnitOfWork, hasher: StringHasher, auth_service: AuthService):
        self._uow = uow
        self._hasher = hasher
        self._auth_service = auth_service

    async def execute(self, *, dto: UserRegisterRequest) -> TokenPairResponse:
        async with self._uow:
            existing_email = await self._uow.users.get_by_email(email=dto.email)
            if existing_email:
                raise EmailTakenError("Пользователь с таким E-mail уже зарегистрирован.")

            existing_username = await self._uow.users.get_by_username(username=dto.username)
            if existing_username:
                raise UsernameTakenError("Это имя пользователя уже зарегистрировано.")

            # register user
            password_hash = self._hasher.hash(raw=dto.password.strip())
            new_user = User(
                email=dto.email,
                username=dto.username,
                password_hash=password_hash,
                registered_at=datetime.datetime.now(UTC),
            )
            saved_user = await self._uow.users.save(user=new_user)

            # create minecraft profile
            new_mc_profile = MinecraftProfile(user_id=saved_user.id, nickname=dto.username, uuid=uuid.uuid4())
            await self._uow.minecraft_profiles.save(profile=new_mc_profile)

            # log in
            session_tokens = self._auth_service.create_session_and_tokens(user_id=saved_user.id)
            session_tokens.session.user_agent = dto.user_agent
            session_tokens.session.ip_address = dto.ip_address
            session_tokens.session.last_used_at = datetime.datetime.now(UTC)
            await self._uow.sessions.save(session=session_tokens.session)

            await self._uow.commit()
            return session_tokens.tokens

from dataclasses import dataclass

from application.decorators.auth import require_login, require_not_banned
from application.dtos.common import StatusResponse
from domain.entities.user import User
from domain.exceptions.auth import InvalidCredentialError
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ChangePasswordRequest:
    old_password: str
    new_password: str


class ChangePasswordUseCase:
    def __init__(self, *, uow: UnitOfWork, hasher: StringHasher):
        self._uow = uow
        self._hasher = hasher

    @require_login
    @require_not_banned
    async def execute(self, *, dto: ChangePasswordRequest, user: User) -> StatusResponse:
        if not self._hasher.verify(raw=dto.old_password, hashed=user.password_hash):
            raise InvalidCredentialError("Неверный текущий пароль.")

        new_password_hash = self._hasher.hash(raw=dto.new_password)
        user.password_hash = new_password_hash
        async with self._uow:
            await self._uow.users.save(user=user)
            await self._uow.commit()
            return StatusResponse()

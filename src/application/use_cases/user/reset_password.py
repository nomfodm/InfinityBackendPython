from dataclasses import dataclass

from application.dtos.common import StatusResponse
from domain.entities.base import Email
from domain.entities.verification_code import VerificationCodePurpose
from domain.exceptions.user import InvalidVerificationCode
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ResetPasswordRequest:
    email: Email
    verification_code: str
    new_password: str


class ResetPasswordUseCase:
    def __init__(self, *, uow: UnitOfWork, hasher: StringHasher):
        self._uow = uow
        self._hasher = hasher

    async def execute(self, *, dto: ResetPasswordRequest) -> StatusResponse:
        async with self._uow:
            code = await self._uow.verification_codes.get_code(
                email=dto.email,
                purpose=VerificationCodePurpose.PASSWORD_RESET,
            )
            if not code or code != dto.verification_code:
                raise InvalidVerificationCode("Неверный код подтверждения.")

            user = await self._uow.users.get_by_email(email=dto.email)
            user.password_hash = self._hasher.hash(raw=dto.new_password)

            await self._uow.users.save(user=user)
            await self._uow.commit()
            return StatusResponse()

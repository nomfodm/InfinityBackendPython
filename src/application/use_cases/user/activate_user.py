from dataclasses import dataclass

from application.dtos.common import StatusResponse
from domain.entities.base import Email
from domain.entities.verification_code import VerificationCodePurpose
from domain.exceptions.user import InvalidVerificationCode
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class ActivateUserRequest:
    email: Email
    verification_code: str


class ActivateUserUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, *, dto: ActivateUserRequest) -> StatusResponse:
        async with self._uow:
            code = await self._uow.verification_codes.get_code(
                email=dto.email, purpose=VerificationCodePurpose.ACTIVATION
            )
            if code is None or code != dto.verification_code:
                raise InvalidVerificationCode("Неверный код подтверждения.")

            user = await self._uow.users.get_by_email(email=dto.email)
            user.is_active = True

            await self._uow.users.save(user=user)

            await self._uow.commit()
            return StatusResponse()

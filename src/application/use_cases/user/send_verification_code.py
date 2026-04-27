import datetime
from dataclasses import dataclass
from datetime import UTC, timedelta

from application.constants import VERIFICATION_CODE_TTL_SECONDS
from application.decorators.auth import require_not_banned
from domain.entities.user import User
from domain.entities.verification_code import VerificationCodePurpose
from domain.interfaces.services.code_generator import CodeGenerator
from domain.interfaces.services.email_service import EmailService
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class SendVerificationCodeRequest:
    purpose: VerificationCodePurpose


@dataclass(frozen=True)
class VerificationCodeResponse:
    email: str
    expires_at: datetime.datetime


class SendVerificationCodeUseCase:
    def __init__(self, *, uow: UnitOfWork, email_service: EmailService, code_generator: CodeGenerator):
        self._uow = uow
        self._email_service = email_service
        self._code_generator = code_generator

    @require_not_banned
    async def execute(self, *, dto: SendVerificationCodeRequest, user: User) -> VerificationCodeResponse:
        verification_code = self._code_generator.generate()

        async with self._uow:
            await self._uow.verification_codes.save_code(
                email=user.email, purpose=dto.purpose, code=verification_code, ttl=VERIFICATION_CODE_TTL_SECONDS
            )

            await self._uow.commit()

        await self._email_service.send_verification_code(email=user.email, code=verification_code)
        return VerificationCodeResponse(
            email=user.email.value,
            expires_at=datetime.datetime.now(UTC) + timedelta(seconds=VERIFICATION_CODE_TTL_SECONDS),
        )

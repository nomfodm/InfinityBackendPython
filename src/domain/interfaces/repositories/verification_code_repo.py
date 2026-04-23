from typing import Protocol

from domain.entities.base import Email
from domain.entities.verification_code import VerificationCodePurpose


class VerificationCodeRepository(Protocol):
    async def save_code(self, *, email: Email, purpose: VerificationCodePurpose, code: str, ttl: int) -> None:
        pass

    async def get_code(self, *, email: Email, purpose: VerificationCodePurpose) -> str | None:
        pass


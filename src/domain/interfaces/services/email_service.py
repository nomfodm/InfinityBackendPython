from typing import Protocol

from domain.entities.base import Email


class EmailService(Protocol):
    async def send_verification_code(self, *, email: Email, code: str) -> None:
        pass

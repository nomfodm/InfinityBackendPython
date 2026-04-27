from domain.entities.base import Email


class ConsoleEmailService:
    async def send_verification_code(self, *, email: Email, code: str) -> None:
        print(f"[EMAIL] To: {email.value} | Verification code: {code}")

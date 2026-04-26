from redis.asyncio import Redis

from domain.entities.base import Email
from domain.entities.verification_code import VerificationCodePurpose
from domain.interfaces.repositories.verification_code_repo import VerificationCodeRepository


class RedisVerificationCodeRepository(VerificationCodeRepository):
    def __init__(self, client: Redis) -> None:
        self._client = client

    def _key(self, email: Email, purpose: VerificationCodePurpose) -> str:
        return f"verification:{email.value}:{purpose.value}"

    async def save_code(self, email: Email, purpose: VerificationCodePurpose, code: str, ttl: int) -> None:
        await self._client.setex(self._key(email, purpose), ttl, code)

    async def get_code(self, email: Email, purpose: VerificationCodePurpose) -> str | None:
        return await self._client.get(self._key(email, purpose))

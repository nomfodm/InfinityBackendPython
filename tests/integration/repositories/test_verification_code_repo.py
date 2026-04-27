from domain.entities.base import Email
from domain.entities.verification_code import VerificationCodePurpose
from infrastructure.redis.verification_code_repo import RedisVerificationCodeRepository


async def test_save_and_get_returns_code(redis_client):
    repo = RedisVerificationCodeRepository(redis_client)
    email = Email("test@test.com")

    await repo.save_code(email=email, purpose=VerificationCodePurpose.ACTIVATION, code="123456", ttl=300)
    result = await repo.get_code(email=email, purpose=VerificationCodePurpose.ACTIVATION)

    assert result == "123456"


async def test_get_returns_none_when_not_saved(redis_client):
    repo = RedisVerificationCodeRepository(redis_client)

    result = await repo.get_code(email=Email("ghost@test.com"), purpose=VerificationCodePurpose.ACTIVATION)

    assert result is None


async def test_different_purposes_have_separate_keys(redis_client):
    repo = RedisVerificationCodeRepository(redis_client)
    email = Email("test@test.com")

    await repo.save_code(email=email, purpose=VerificationCodePurpose.ACTIVATION, code="111111", ttl=300)
    await repo.save_code(email=email, purpose=VerificationCodePurpose.PASSWORD_RESET, code="999999", ttl=300)

    assert await repo.get_code(email=email, purpose=VerificationCodePurpose.ACTIVATION) == "111111"
    assert await repo.get_code(email=email, purpose=VerificationCodePurpose.PASSWORD_RESET) == "999999"


async def test_overwrite_replaces_previous_code(redis_client):
    repo = RedisVerificationCodeRepository(redis_client)
    email = Email("test@test.com")

    await repo.save_code(email=email, purpose=VerificationCodePurpose.ACTIVATION, code="111111", ttl=300)
    await repo.save_code(email=email, purpose=VerificationCodePurpose.ACTIVATION, code="222222", ttl=300)
    result = await repo.get_code(email=email, purpose=VerificationCodePurpose.ACTIVATION)

    assert result == "222222"

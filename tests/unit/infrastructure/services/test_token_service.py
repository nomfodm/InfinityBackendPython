import pytest

from domain.exceptions.session import TokenAuthenticityError
from infrastructure.services.token_service import JWTTokenService

SECRET = "test-secret-key-that-is-long-enough-for-hs256"


@pytest.fixture
def service():
    return JWTTokenService(secret_key=SECRET)


def test_generate_and_decode_access_token(service):
    token = service.generate_access_token({"user_id": 42}, expires_in_minutes=15)
    payload = service.decode_access_token(token)

    assert payload["user_id"] == 42


def test_decode_access_token_expired(service):
    token = service.generate_access_token({"user_id": 1}, expires_in_minutes=-10)

    with pytest.raises(TokenAuthenticityError):
        service.decode_access_token(token)


def test_decode_access_token_wrong_secret(service):
    token = service.generate_access_token({"user_id": 1}, expires_in_minutes=15)
    other = JWTTokenService(secret_key="different-secret")

    with pytest.raises(TokenAuthenticityError):
        other.decode_access_token(token)


def test_decode_access_token_tampered(service):
    token = service.generate_access_token({"user_id": 1}, expires_in_minutes=15)
    tampered = token[:-5] + "XXXXX"

    with pytest.raises(TokenAuthenticityError):
        service.decode_access_token(tampered)


def test_generate_refresh_token_is_long_string(service):
    token = service.generate_refresh_token()

    assert isinstance(token, str)
    assert len(token) > 32


def test_generate_refresh_token_unique(service):
    t1 = service.generate_refresh_token()
    t2 = service.generate_refresh_token()

    assert t1 != t2

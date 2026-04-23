import datetime
import uuid
from datetime import timedelta
from typing import cast

import pytest
from pytest_mock import MockerFixture

from application.constants import ACCESS_TOKEN_EXPIRES_MINUTES, REFRESH_TOKEN_EXPIRES_DAYS
from application.dtos.auth import TokenPairResponse
from application.services.auth import AuthService, SessionTokensDTO
from domain.entities.session import Session
from domain.exceptions.session import (
    SessionExpiredError,
    SessionNotFoundError,
    SessionRevokedError,
    TokenAuthenticityError,
)
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.services.token_service import TokenService


@pytest.fixture
def mock_token_service(mocker: MockerFixture) -> TokenService:
    mock = mocker.MagicMock()

    mock.generate_access_token.return_value = "access_token"
    mock.generate_refresh_token.return_value = "refresh_token"

    return cast(TokenService, mock)


@pytest.fixture
def mock_hasher_service(mocker: MockerFixture) -> StringHasher:
    mock = mocker.MagicMock()

    mock.hash.side_effect = lambda raw: f"[hashed]{raw}"
    mock.verify.return_value = True

    return cast(StringHasher, mock)


@pytest.fixture
def service(mock_token_service: TokenService, mock_hasher_service: StringHasher):
    return AuthService(token_service=mock_token_service, token_hasher=mock_hasher_service)


def test_generate_access_token(service: AuthService, mock_token_service: TokenService):
    result = service.generate_access_token(user_id=1)

    assert result == "access_token"

    mock_token_service.generate_access_token.assert_called_once_with(
        data={"sub": "1"}, expires_in_minutes=ACCESS_TOKEN_EXPIRES_MINUTES
    )


def test_generate_refresh_token(service: AuthService, mock_token_service: TokenService):
    result = service.generate_refresh_token()

    assert result[0] == "refresh_token"
    assert isinstance(result[1], datetime.datetime)
    assert result[2] == "[hashed]refresh_token"

    mock_token_service.generate_refresh_token.assert_called_once()


def test_verify_session_success(service: AuthService, fake_session: Session):
    fake_session.expires_at += timedelta(days=1)
    service.verify_session(refresh_token="refresh_token", session=fake_session)


def test_verify_session_fails_not_found(service: AuthService):
    with pytest.raises(SessionNotFoundError):
        service.verify_session(refresh_token="refresh_token", session=None)


def test_verify_session_fails_revoked(service: AuthService, fake_session: Session):
    fake_session.is_revoked = True
    with pytest.raises(SessionRevokedError):
        service.verify_session(refresh_token="refresh_token", session=fake_session)


def test_verify_session_fails_expired(service: AuthService, fake_session: Session):
    fake_session.expires_at -= timedelta(days=5)
    with pytest.raises(SessionExpiredError):
        service.verify_session(refresh_token="refresh_token", session=fake_session)


def test_verify_session_fails_not_verified(
    service: AuthService, fake_session: Session, mock_hasher_service: StringHasher
):
    mock_hasher_service.verify.return_value = False
    with pytest.raises(TokenAuthenticityError):
        service.verify_session(refresh_token="refresh_token", session=fake_session)


def test_create_session_and_tokens(mocker: MockerFixture, service: AuthService):
    fixed_uuid = uuid.uuid4()
    fixed_date = datetime.datetime(2000, 10, 10)
    mocker.patch("uuid.uuid4", return_value=fixed_uuid)

    mock_datetime = mocker.patch("application.services.auth.datetime")
    mock_datetime.datetime.now.return_value = fixed_date

    result = service.create_session_and_tokens(user_id=1)

    assert result == SessionTokensDTO(
        tokens=TokenPairResponse(access_token="access_token", refresh_split_token=f"{fixed_uuid}.refresh_token"),
        session=Session(
            refresh_token_hash="[hashed]refresh_token",
            expires_at=fixed_date + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS),
            user_id=1,
            id=fixed_uuid,
        ),
    )

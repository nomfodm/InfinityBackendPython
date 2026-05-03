from typing import cast
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from application.services.auth import AuthService
from application.use_cases.auth.login import LoginUseCase, UserLoginRequest
from domain.entities.base import UserRelatedHandle
from domain.entities.user import User
from domain.exceptions.auth import InvalidCredentialError
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def uc(mock_hasher: StringHasher, mock_auth_service: AuthService, mock_uow: UnitOfWork):
    return LoginUseCase(uow=mock_uow, hasher=mock_hasher, auth_service=mock_auth_service)


@pytest.fixture
def dto():
    return UserLoginRequest(
        username=UserRelatedHandle("tester"),
        password="password",
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1",
    )


@pytest.fixture
def mock_uow(mock_uow: UnitOfWork, fake_user: User):
    mock_uow.users.get_by_username = AsyncMock(return_value=fake_user)

    return mock_uow


@pytest.fixture
def mock_hasher(mocker: MockerFixture) -> StringHasher:
    mock_hasher = mocker.MagicMock()

    mock_hasher.verify.return_value = True

    return cast(StringHasher, mock_hasher)


@pytest.mark.asyncio
async def test_login_success(
    mock_uow: UnitOfWork, uc: LoginUseCase, mock_auth_service: AuthService, dto: UserLoginRequest
):
    result = await uc.execute(dto=dto)

    mock_auth_service.create_session_and_tokens.assert_called_once_with(user_id=1)

    assert result.access_token == "access_token"
    assert result.refresh_split_token == "uuid.refresh_token"

    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_login_success_fails_invalid_credential_by_user(
    mock_uow: UnitOfWork, uc: LoginUseCase, dto: UserLoginRequest
):
    mock_uow.users.get_by_username.return_value = None

    with pytest.raises(InvalidCredentialError):
        await uc.execute(dto=dto)

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_login_saves_user_agent_and_ip_address(
    mock_uow: UnitOfWork, uc: LoginUseCase, mock_auth_service: AuthService, dto: UserLoginRequest
):
    await uc.execute(dto=dto)

    session_tokens = mock_auth_service.create_session_and_tokens.return_value
    assert session_tokens.session.user_agent == "Mozilla/5.0"
    assert session_tokens.session.ip_address == "127.0.0.1"


@pytest.mark.asyncio
async def test_login_deletes_invalid_sessions(
    mock_uow: UnitOfWork, uc: LoginUseCase, fake_user: User, dto: UserLoginRequest
):
    await uc.execute(dto=dto)

    mock_uow.sessions.delete_invalid_by_user_id.assert_awaited_once_with(user_id=fake_user.id)


@pytest.mark.asyncio
async def test_login_success_fails_invalid_credential_by_hasher(
    mock_uow: UnitOfWork, uc: LoginUseCase, mock_hasher: StringHasher, dto: UserLoginRequest
):
    mock_hasher.verify.return_value = False

    with pytest.raises(InvalidCredentialError):
        await uc.execute(dto=dto)

    mock_uow.commit.assert_not_called()

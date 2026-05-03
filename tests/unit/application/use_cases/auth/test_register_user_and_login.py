from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from application.services.auth import AuthService
from application.use_cases.auth.register_user_and_login import RegisterUserAndLoginUseCase, UserRegisterRequest
from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import User
from domain.exceptions.auth import EmailTakenError, UsernameTakenError
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def uc(mocker: MockerFixture, mock_auth_service: AuthService, mock_uow: UnitOfWork):
    return RegisterUserAndLoginUseCase(uow=mock_uow, hasher=mocker.MagicMock(), auth_service=mock_auth_service)


@pytest.fixture
def dto():
    return UserRegisterRequest(
        email=Email("test@a.com"),
        username=UserRelatedHandle("tester"),
        password="123",
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1",
    )


@pytest.fixture
def mock_uow(mock_uow: UnitOfWork, fake_user: User):
    mock_uow.users.get_by_email = AsyncMock(return_value=None)
    mock_uow.users.get_by_username = AsyncMock(return_value=None)
    mock_uow.users.save = AsyncMock(return_value=fake_user)

    return mock_uow


@pytest.mark.asyncio
async def test_register_user_and_login_success(
    mock_uow: UnitOfWork, uc: RegisterUserAndLoginUseCase, mock_auth_service: AuthService, dto: UserRegisterRequest
) -> None:
    result = await uc.execute(dto=dto)

    mock_auth_service.create_session_and_tokens.assert_called_once_with(user_id=1)

    assert result.access_token == "access_token"
    assert result.refresh_split_token == "uuid.refresh_token"

    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_register_creates_minecraft_profile(
    mock_uow: UnitOfWork, uc: RegisterUserAndLoginUseCase, fake_user: User, dto: UserRegisterRequest
) -> None:
    await uc.execute(dto=dto)

    mock_uow.minecraft_profiles.save.assert_awaited_once()
    saved_profile = mock_uow.minecraft_profiles.save.call_args.kwargs["profile"]
    assert saved_profile.user_id == fake_user.id
    assert saved_profile.nickname == dto.username


@pytest.mark.asyncio
async def test_register_saves_user_agent_and_ip_address(
    mock_uow: UnitOfWork, uc: RegisterUserAndLoginUseCase, mock_auth_service: AuthService, dto: UserRegisterRequest
) -> None:
    await uc.execute(dto=dto)

    session_tokens = mock_auth_service.create_session_and_tokens.return_value
    assert session_tokens.session.user_agent == "Mozilla/5.0"
    assert session_tokens.session.ip_address == "127.0.0.1"


@pytest.mark.asyncio
async def test_register_user_and_login_fails_email_taken(
    mock_uow: UnitOfWork, fake_user: User, uc: RegisterUserAndLoginUseCase, dto: UserRegisterRequest
) -> None:
    mock_uow.users.get_by_email = AsyncMock(return_value=fake_user)

    with pytest.raises(EmailTakenError):
        await uc.execute(dto=dto)

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_register_user_and_login_fails_username_taken(
    mock_uow: UnitOfWork, fake_user: User, uc: RegisterUserAndLoginUseCase, dto: UserRegisterRequest
) -> None:
    mock_uow.users.get_by_username = AsyncMock(return_value=fake_user)

    with pytest.raises(UsernameTakenError):
        await uc.execute(dto=dto)

    mock_uow.commit.assert_not_called()

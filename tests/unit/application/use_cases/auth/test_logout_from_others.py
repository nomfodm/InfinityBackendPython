import uuid
from typing import cast
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from application.dtos.auth import SessionCredentials
from application.services.auth import AuthService
from application.use_cases.auth.logout_from_others import LogoutFromOthersRequest, LogoutFromOthersUseCase
from domain.entities.session import Session
from domain.entities.user import User
from domain.exceptions.auth import AccessDeniedError
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def mock_hasher(mocker: MockerFixture) -> StringHasher:
    mock = mocker.MagicMock(spec=StringHasher)
    mock.verify.return_value = True
    return cast(StringHasher, mock)


@pytest.fixture
def uc(mock_auth_service: AuthService, mock_uow: UnitOfWork, mock_hasher: StringHasher):
    return LogoutFromOthersUseCase(uow=mock_uow, auth_service=mock_auth_service, hasher=mock_hasher)


@pytest.fixture
def dto():
    return LogoutFromOthersRequest(
        password="correct_password",
        session_credentials=SessionCredentials(id=uuid.uuid4(), refresh_token="refresh_token"),
    )


@pytest.fixture
def mock_uow(mock_uow: UnitOfWork, fake_session: Session, fake_user: User):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=fake_session)
    mock_uow.users.get_by_id = AsyncMock(return_value=fake_user)
    return mock_uow


@pytest.mark.asyncio
async def test_logout_from_others_success(
    mock_uow: UnitOfWork, uc: LogoutFromOthersUseCase, dto: LogoutFromOthersRequest, fake_session: Session
):
    await uc.execute(dto=dto)

    mock_uow.sessions.delete_others_by_user_id.assert_awaited_once_with(
        user_id=fake_session.user_id, exclude_session_id=fake_session.id
    )
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_logout_from_others_fails_on_wrong_password(
    mock_uow: UnitOfWork, mock_auth_service: AuthService, fake_session: Session, fake_user: User, mocker
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=fake_session)
    mock_uow.users.get_by_id = AsyncMock(return_value=fake_user)
    hasher = mocker.MagicMock(spec=StringHasher)
    hasher.verify.return_value = False
    uc = LogoutFromOthersUseCase(uow=mock_uow, auth_service=mock_auth_service, hasher=hasher)

    with pytest.raises(AccessDeniedError):
        await uc.execute(
            dto=LogoutFromOthersRequest(
                password="wrong_password",
                session_credentials=SessionCredentials(id=uuid.uuid4(), refresh_token="refresh_token"),
            )
        )

    mock_uow.commit.assert_not_called()

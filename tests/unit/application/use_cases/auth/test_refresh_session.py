import uuid
from unittest.mock import AsyncMock

import pytest

from application.dtos.auth import SessionCredentials
from application.services.auth import AuthService
from application.use_cases.auth.refresh_session import RefreshSessionUseCase
from domain.entities.session import Session
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def uc(mock_auth_service: AuthService, mock_uow: UnitOfWork):
    return RefreshSessionUseCase(uow=mock_uow, auth_service=mock_auth_service)


@pytest.fixture
def dto():
    return SessionCredentials(id=uuid.uuid4(), refresh_token="refresh_token")


@pytest.fixture
def mock_uow(mock_uow: UnitOfWork, fake_session: Session):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=fake_session)

    return mock_uow


@pytest.mark.asyncio
async def test_refresh_session_success(
    mock_uow: UnitOfWork,
    uc: RefreshSessionUseCase,
    mock_auth_service: AuthService,
    dto: SessionCredentials,
    fake_session: Session,
):
    result = await uc.execute(dto=dto)

    mock_auth_service.generate_access_token.assert_called_once_with(user_id=1)
    mock_auth_service.generate_refresh_token.assert_called_once()

    assert result.access_token == "access_token"
    assert result.refresh_split_token == f"{fake_session.id}.refresh_token"

    assert fake_session.refresh_token_hash == "refresh_token_hash"
    mock_uow.sessions.save.assert_awaited_once_with(session=fake_session)
    mock_uow.commit.assert_called_once()

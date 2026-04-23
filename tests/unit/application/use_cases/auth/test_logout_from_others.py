import uuid

import pytest

from application.dtos.auth import SessionCredentials
from application.services.auth import AuthService
from application.use_cases.auth.logout_from_others import LogoutFromOthersUseCase
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def uc(mock_auth_service: AuthService, mock_uow: UnitOfWork):
    return LogoutFromOthersUseCase(uow=mock_uow, auth_service=mock_auth_service)


@pytest.fixture
def dto():
    return SessionCredentials(
        id=uuid.uuid4(),
        refresh_token="refresh_token"
    )


@pytest.mark.asyncio
async def test_logout_from_others_success(mock_uow: UnitOfWork,
                                          uc: LogoutFromOthersUseCase,
                                          dto: SessionCredentials):
    await uc.execute(dto=dto)

    mock_uow.commit.assert_called_once()
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from application.dtos.auth import SessionCredentials
from application.services.auth import AuthService
from application.use_cases.auth.get_login_history import GetLoginHistoryUseCase
from domain.entities.login_history import LoginHistoryEntry
from domain.entities.session import Session
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def mock_auth_service() -> AuthService:
    service = MagicMock(spec=AuthService)
    service.verify_session.return_value = None
    return service


@pytest.fixture
def session() -> Session:
    return Session(
        id=uuid.uuid4(),
        user_id=1,
        refresh_token_hash="hash",
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )


@pytest.fixture
def dto(session: Session) -> SessionCredentials:
    return SessionCredentials(id=session.id, refresh_token="refresh_token")


@pytest.fixture
def uc(mock_uow: UnitOfWork, mock_auth_service: AuthService) -> GetLoginHistoryUseCase:
    return GetLoginHistoryUseCase(uow=mock_uow, auth_service=mock_auth_service)


@pytest.fixture
def fake_entries() -> list[LoginHistoryEntry]:
    return [
        LoginHistoryEntry(
            id=1, user_id=1, timestamp=datetime.now(UTC), ip_address="127.0.0.1", user_agent="launcher/1.0"
        ),
        LoginHistoryEntry(id=2, user_id=1, timestamp=datetime.now(UTC), ip_address="10.0.0.1", user_agent=None),
    ]


@pytest.mark.asyncio
async def test_get_login_history_success(
    mock_uow: UnitOfWork,
    uc: GetLoginHistoryUseCase,
    session: Session,
    dto: SessionCredentials,
    fake_entries: list[LoginHistoryEntry],
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=session)
    mock_uow.login_history.get_by_user_id = AsyncMock(return_value=fake_entries)

    result = await uc.execute(dto=dto)

    assert len(result) == 2
    assert result[0].ip_address == "127.0.0.1"
    assert result[1].user_agent is None
    mock_uow.login_history.get_by_user_id.assert_awaited_once_with(user_id=session.user_id)


@pytest.mark.asyncio
async def test_get_login_history_returns_empty_list(
    mock_uow: UnitOfWork,
    uc: GetLoginHistoryUseCase,
    session: Session,
    dto: SessionCredentials,
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=session)
    mock_uow.login_history.get_by_user_id = AsyncMock(return_value=[])

    result = await uc.execute(dto=dto)

    assert result == []


@pytest.mark.asyncio
async def test_get_login_history_verifies_session(
    mock_uow: UnitOfWork,
    uc: GetLoginHistoryUseCase,
    mock_auth_service: AuthService,
    session: Session,
    dto: SessionCredentials,
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=session)
    mock_uow.login_history.get_by_user_id = AsyncMock(return_value=[])
    mock_auth_service.verify_session.side_effect = Exception("invalid session")

    with pytest.raises(Exception, match="invalid session"):
        await uc.execute(dto=dto)

    mock_uow.login_history.get_by_user_id.assert_not_called()

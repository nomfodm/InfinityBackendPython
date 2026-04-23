import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from application.dtos.auth import SessionCredentials
from application.services.auth import AuthService
from application.use_cases.auth.get_sessions import GetSessionsUseCase
from domain.entities.session import Session
from domain.interfaces.unit_of_work import UnitOfWork


def _session(user_id: int = 1, **kwargs) -> Session:
    return Session(
        id=uuid.uuid4(),
        user_id=user_id,
        refresh_token_hash="hash",
        expires_at=datetime.now(UTC) + timedelta(days=1),
        **kwargs,
    )


@pytest.fixture
def current_session() -> Session:
    return _session(user_agent="Infinity Launcher 1.0.0", ip_address="1.2.3.4")


@pytest.fixture
def other_session() -> Session:
    return _session(user_agent="Chrome/Windows", ip_address="5.6.7.8")


@pytest.fixture
def dto(current_session: Session) -> SessionCredentials:
    return SessionCredentials(id=current_session.id, refresh_token="refresh_token")


@pytest.mark.asyncio
async def test_get_sessions_returns_all_user_sessions(
    mock_uow: UnitOfWork,
    mock_auth_service: AuthService,
    current_session: Session,
    other_session: Session,
    dto: SessionCredentials,
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=current_session)
    mock_uow.sessions.get_all_by_user_id = AsyncMock(return_value=[current_session, other_session])

    result = await GetSessionsUseCase(uow=mock_uow, auth_service=mock_auth_service).execute(dto=dto)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_sessions_marks_current_session(
    mock_uow: UnitOfWork,
    mock_auth_service: AuthService,
    current_session: Session,
    other_session: Session,
    dto: SessionCredentials,
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=current_session)
    mock_uow.sessions.get_all_by_user_id = AsyncMock(return_value=[current_session, other_session])

    result = await GetSessionsUseCase(uow=mock_uow, auth_service=mock_auth_service).execute(dto=dto)

    current = next(r for r in result if r.id == current_session.id)
    other = next(r for r in result if r.id == other_session.id)
    assert current.is_current is True
    assert other.is_current is False


@pytest.mark.asyncio
async def test_get_sessions_maps_fields(
    mock_uow: UnitOfWork,
    mock_auth_service: AuthService,
    current_session: Session,
    dto: SessionCredentials,
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=current_session)
    mock_uow.sessions.get_all_by_user_id = AsyncMock(return_value=[current_session])

    result = await GetSessionsUseCase(uow=mock_uow, auth_service=mock_auth_service).execute(dto=dto)

    assert result[0].user_agent == "Infinity Launcher 1.0.0"
    assert result[0].ip_address == "1.2.3.4"
    assert result[0].id == current_session.id

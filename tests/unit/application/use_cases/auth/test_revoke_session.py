import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from application.dtos.auth import SessionCredentials
from application.services.auth import AuthService
from application.use_cases.auth.revoke_session import RevokeSessionRequest, RevokeSessionUseCase
from domain.entities.session import Session
from domain.exceptions.session import CannotRevokeSessionError
from domain.interfaces.unit_of_work import UnitOfWork


def _session(user_id: int = 1) -> Session:
    return Session(
        id=uuid.uuid4(),
        user_id=user_id,
        refresh_token_hash="hash",
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )


@pytest.fixture
def current_session() -> Session:
    return _session(user_id=1)


@pytest.fixture
def other_session() -> Session:
    return _session(user_id=1)


@pytest.fixture
def dto(current_session: Session, other_session: Session) -> RevokeSessionRequest:
    return RevokeSessionRequest(
        session_credentials=SessionCredentials(id=current_session.id, refresh_token="refresh_token"),
        session_id_to_revoke=other_session.id,
    )


@pytest.mark.asyncio
async def test_revoke_session_success(
    mock_uow: UnitOfWork,
    mock_auth_service: AuthService,
    current_session: Session,
    other_session: Session,
    dto: RevokeSessionRequest,
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(side_effect=[current_session, other_session])

    result = await RevokeSessionUseCase(uow=mock_uow, auth_service=mock_auth_service).execute(dto=dto)

    assert result.ok is True
    assert other_session.is_revoked is True
    mock_uow.sessions.save.assert_awaited_once_with(session=other_session)
    mock_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_session_fails_when_revoking_own(
    mock_uow: UnitOfWork,
    mock_auth_service: AuthService,
    current_session: Session,
):
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(return_value=current_session)
    dto = RevokeSessionRequest(
        session_credentials=SessionCredentials(id=current_session.id, refresh_token="refresh_token"),
        session_id_to_revoke=current_session.id,
    )

    with pytest.raises(CannotRevokeSessionError):
        await RevokeSessionUseCase(uow=mock_uow, auth_service=mock_auth_service).execute(dto=dto)

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_revoke_session_fails_when_different_owner(
    mock_uow: UnitOfWork,
    mock_auth_service: AuthService,
    current_session: Session,
):
    foreign_session = _session(user_id=999)
    mock_uow.sessions.get_by_id_or_raise = AsyncMock(side_effect=[current_session, foreign_session])
    dto = RevokeSessionRequest(
        session_credentials=SessionCredentials(id=current_session.id, refresh_token="refresh_token"),
        session_id_to_revoke=foreign_session.id,
    )

    with pytest.raises(CannotRevokeSessionError):
        await RevokeSessionUseCase(uow=mock_uow, auth_service=mock_auth_service).execute(dto=dto)

    mock_uow.sessions.save.assert_not_called()
    mock_uow.commit.assert_not_called()

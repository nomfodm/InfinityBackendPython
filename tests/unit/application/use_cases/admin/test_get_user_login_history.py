from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from application.use_cases.admin.get_user_login_history import GetUserLoginHistoryRequest, GetUserLoginHistoryUseCase
from domain.entities.base import Email, UserRelatedHandle
from domain.entities.login_history import LoginHistoryEntry
from domain.entities.user import Role, User
from domain.exceptions.auth import AccessDeniedError
from domain.exceptions.user import UserNotFoundError
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def admin_user(active_user: User) -> User:
    active_user.roles = {Role.ADMIN}
    return active_user


@pytest.fixture
def target_user() -> User:
    return User(
        id=2,
        email=Email("target@test.com"),
        username=UserRelatedHandle("target"),
        password_hash="hash",
        registered_at=datetime.now(UTC),
        is_active=True,
    )


@pytest.fixture
def uc(mock_uow: UnitOfWork) -> GetUserLoginHistoryUseCase:
    return GetUserLoginHistoryUseCase(uow=mock_uow)


@pytest.mark.asyncio
async def test_get_user_login_history_success(
    mock_uow: UnitOfWork, uc: GetUserLoginHistoryUseCase, admin_user: User, target_user: User
):
    entries = [LoginHistoryEntry(id=1, user_id=2, timestamp=datetime.now(UTC), ip_address="1.2.3.4")]
    mock_uow.users.get_by_id = AsyncMock(return_value=target_user)
    mock_uow.login_history.get_by_user_id = AsyncMock(return_value=entries)
    dto = GetUserLoginHistoryRequest(user_id=2)

    result = await uc.execute(dto=dto, user=admin_user)

    assert len(result) == 1
    assert result[0].ip_address == "1.2.3.4"
    mock_uow.login_history.get_by_user_id.assert_awaited_once_with(user_id=2)


@pytest.mark.asyncio
async def test_get_user_login_history_raises_when_user_not_found(
    mock_uow: UnitOfWork, uc: GetUserLoginHistoryUseCase, admin_user: User
):
    mock_uow.users.get_by_id = AsyncMock(return_value=None)
    dto = GetUserLoginHistoryRequest(user_id=999)

    with pytest.raises(UserNotFoundError):
        await uc.execute(dto=dto, user=admin_user)

    mock_uow.login_history.get_by_user_id.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_login_history_raises_for_non_admin(
    mock_uow: UnitOfWork, uc: GetUserLoginHistoryUseCase, active_user: User
):
    dto = GetUserLoginHistoryRequest(user_id=2)

    with pytest.raises(AccessDeniedError):
        await uc.execute(dto=dto, user=active_user)

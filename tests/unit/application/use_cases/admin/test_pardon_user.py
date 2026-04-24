from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from application.use_cases.admin.pardon_user import PardonUserRequest, PardonUserUseCase
from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import BanStatus, Role, User
from domain.exceptions.auth import AccessDeniedError
from domain.exceptions.user import UserNotFoundError
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def admin_user(active_user: User) -> User:
    active_user.roles = {Role.ADMIN}
    return active_user


@pytest.fixture
def banned_user() -> User:
    user = User(
        id=2,
        email=Email("banned@test.com"),
        username=UserRelatedHandle("banned"),
        password_hash="hash",
        registered_at=datetime.now(UTC),
        is_active=True,
    )
    user.ban_status = BanStatus(is_banned=True, is_permanent=True, admin_user_id=99)
    return user


@pytest.fixture
def uc(mock_uow: UnitOfWork) -> PardonUserUseCase:
    return PardonUserUseCase(uow=mock_uow)


@pytest.mark.asyncio
async def test_pardon_user_success(mock_uow: UnitOfWork, uc: PardonUserUseCase, admin_user: User, banned_user: User):
    mock_uow.users.get_by_id = AsyncMock(return_value=banned_user)
    dto = PardonUserRequest(user_id=banned_user.id)

    result = await uc.execute(dto=dto, user=admin_user)

    assert result.ok is True
    assert banned_user.ban_status.is_banned is False
    assert banned_user.ban_status.is_permanent is False
    assert banned_user.ban_status.banned_till is None
    assert banned_user.ban_status.admin_user_id == admin_user.id
    mock_uow.users.save.assert_awaited_once_with(user=banned_user)
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_pardon_user_raises_when_user_not_found(mock_uow: UnitOfWork, uc: PardonUserUseCase, admin_user: User):
    mock_uow.users.get_by_id = AsyncMock(return_value=None)
    dto = PardonUserRequest(user_id=999)

    with pytest.raises(UserNotFoundError):
        await uc.execute(dto=dto, user=admin_user)

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_pardon_user_raises_for_non_admin(mock_uow: UnitOfWork, uc: PardonUserUseCase, active_user: User):
    dto = PardonUserRequest(user_id=2)

    with pytest.raises(AccessDeniedError):
        await uc.execute(dto=dto, user=active_user)

    mock_uow.commit.assert_not_called()

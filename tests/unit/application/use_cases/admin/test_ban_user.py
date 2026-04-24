from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from application.use_cases.admin.ban_user import BanType, BanUserRequest, BanUserUseCase
from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import Role, User
from domain.exceptions.auth import AccessDeniedError
from domain.exceptions.base import ValidationError
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
def uc(mock_uow: UnitOfWork) -> BanUserUseCase:
    return BanUserUseCase(uow=mock_uow)


@pytest.mark.asyncio
async def test_ban_user_permanent_success(
    mock_uow: UnitOfWork, uc: BanUserUseCase, admin_user: User, target_user: User
):
    mock_uow.users.get_by_id = AsyncMock(return_value=target_user)
    dto = BanUserRequest(ban_type=BanType.PERMANENT, user_to_ban_id=target_user.id)

    result = await uc.execute(dto=dto, user=admin_user)

    assert result.ok is True
    assert target_user.ban_status.is_banned is True
    assert target_user.ban_status.is_permanent is True
    assert target_user.ban_status.admin_user_id == admin_user.id
    mock_uow.users.save.assert_awaited_once_with(user=target_user)
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_ban_user_temporary_success(
    mock_uow: UnitOfWork, uc: BanUserUseCase, admin_user: User, target_user: User
):
    banned_till = datetime.now(UTC) + timedelta(days=7)
    mock_uow.users.get_by_id = AsyncMock(return_value=target_user)
    dto = BanUserRequest(ban_type=BanType.TEMPORARY, user_to_ban_id=target_user.id, banned_till=banned_till)

    result = await uc.execute(dto=dto, user=admin_user)

    assert result.ok is True
    assert target_user.ban_status.is_banned is True
    assert target_user.ban_status.is_permanent is False
    assert target_user.ban_status.banned_till == banned_till
    assert target_user.ban_status.admin_user_id == admin_user.id
    mock_uow.commit.assert_called_once()


def test_ban_user_temporary_without_banned_till_raises_validation_error():
    with pytest.raises(ValidationError):
        BanUserRequest(ban_type=BanType.TEMPORARY, user_to_ban_id=1)


@pytest.mark.asyncio
async def test_ban_user_raises_when_user_not_found(mock_uow: UnitOfWork, uc: BanUserUseCase, admin_user: User):
    mock_uow.users.get_by_id = AsyncMock(return_value=None)
    dto = BanUserRequest(ban_type=BanType.PERMANENT, user_to_ban_id=999)

    with pytest.raises(UserNotFoundError):
        await uc.execute(dto=dto, user=admin_user)

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_ban_user_raises_for_non_admin(mock_uow: UnitOfWork, uc: BanUserUseCase, active_user: User):
    dto = BanUserRequest(ban_type=BanType.PERMANENT, user_to_ban_id=2)

    with pytest.raises(AccessDeniedError):
        await uc.execute(dto=dto, user=active_user)

    mock_uow.commit.assert_not_called()

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from application.use_cases.admin.get_users import GetUsersUseCase
from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import Role, User
from domain.exceptions.auth import AccessDeniedError
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def admin_user(active_user: User) -> User:
    active_user.roles = {Role.ADMIN}
    return active_user


def _make_user(id: int, username: str, email: str) -> User:
    return User(
        id=id,
        email=Email(email),
        username=UserRelatedHandle(username),
        password_hash="hash",
        registered_at=datetime.now(UTC),
        is_active=True,
    )


@pytest.fixture
def uc(mock_uow: UnitOfWork) -> GetUsersUseCase:
    return GetUsersUseCase(uow=mock_uow)


@pytest.mark.asyncio
async def test_get_users_success(mock_uow: UnitOfWork, uc: GetUsersUseCase, admin_user: User):
    users = [_make_user(2, "alice", "alice@test.com"), _make_user(3, "bob1", "bob@test.com")]
    mock_uow.users.get_all = AsyncMock(return_value=users)

    result = await uc.execute(user=admin_user)

    assert len(result) == 2
    assert result[0].username == "alice"
    assert result[1].email == "bob@test.com"
    assert result[0].is_active is True
    mock_uow.users.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_users_raises_for_non_admin(mock_uow: UnitOfWork, uc: GetUsersUseCase, active_user: User):
    with pytest.raises(AccessDeniedError):
        await uc.execute(user=active_user)

    mock_uow.users.get_all.assert_not_called()

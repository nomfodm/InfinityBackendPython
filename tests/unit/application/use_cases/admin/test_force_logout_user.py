import pytest

from application.use_cases.admin.force_logout_user import ForceLogoutUserRequest, ForceLogoutUserUseCase
from domain.entities.user import Role, User
from domain.exceptions.auth import AccessDeniedError
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def admin_user(active_user: User) -> User:
    active_user.roles = {Role.ADMIN}
    return active_user


@pytest.fixture
def uc(mock_uow: UnitOfWork) -> ForceLogoutUserUseCase:
    return ForceLogoutUserUseCase(uow=mock_uow)


@pytest.mark.asyncio
async def test_force_logout_user_success(mock_uow: UnitOfWork, uc: ForceLogoutUserUseCase, admin_user: User):
    dto = ForceLogoutUserRequest(user_id=2)

    result = await uc.execute(dto=dto, user=admin_user)

    assert result.ok is True
    mock_uow.sessions.delete_all_by_user_id.assert_awaited_once_with(user_id=2)
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_force_logout_user_raises_for_non_admin(
    mock_uow: UnitOfWork, uc: ForceLogoutUserUseCase, active_user: User
):
    dto = ForceLogoutUserRequest(user_id=2)

    with pytest.raises(AccessDeniedError):
        await uc.execute(dto=dto, user=active_user)

    mock_uow.sessions.delete_all_by_user_id.assert_not_called()
    mock_uow.commit.assert_not_called()

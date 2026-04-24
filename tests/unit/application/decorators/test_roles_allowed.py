import pytest

from application.decorators.auth import roles_allowed
from domain.entities.user import Role, User
from domain.exceptions.auth import AccessDeniedError, UnauthenticatedError


class _AdminOnlyUC:
    @roles_allowed(Role.ADMIN)
    async def execute(self, *, user: User):
        return "ok"


class _MultiRoleUC:
    @roles_allowed(Role.ADMIN, Role.PLAYER)
    async def execute(self, *, user: User):
        return "ok"


@pytest.mark.asyncio
async def test_roles_allowed_passes_for_admin(active_user: User):
    active_user.roles = {Role.ADMIN}
    result = await _AdminOnlyUC().execute(user=active_user)
    assert result == "ok"


@pytest.mark.asyncio
async def test_roles_allowed_raises_for_player(active_user: User):
    with pytest.raises(AccessDeniedError):
        await _AdminOnlyUC().execute(user=active_user)


@pytest.mark.asyncio
async def test_roles_allowed_raises_when_not_user_instance():
    with pytest.raises(UnauthenticatedError):
        await _AdminOnlyUC().execute(user="not_a_user")


@pytest.mark.asyncio
async def test_roles_allowed_raises_when_user_is_none():
    with pytest.raises(UnauthenticatedError):
        await _AdminOnlyUC().execute(user=None)


@pytest.mark.asyncio
async def test_roles_allowed_passes_when_user_has_one_of_many_roles(active_user: User):
    result = await _MultiRoleUC().execute(user=active_user)
    assert result == "ok"

import pytest

from application.decorators.auth import require_login
from domain.entities.user import BanStatus, User
from domain.exceptions.auth import UnauthenticatedError, UserNeedsActivationError


class _UC:
    @require_login
    async def execute(self, *, user: User):
        return "ok"


@pytest.mark.asyncio
async def test_require_login_passes_for_active_user(active_user: User):
    result = await _UC().execute(user=active_user)
    assert result == "ok"


@pytest.mark.asyncio
async def test_require_login_passes_for_banned_user(active_user: User):
    active_user.ban_status = BanStatus(is_banned=True, is_permanent=True)
    result = await _UC().execute(user=active_user)
    assert result == "ok"


@pytest.mark.asyncio
async def test_require_login_raises_when_not_user_instance():
    with pytest.raises(UnauthenticatedError):
        await _UC().execute(user="not_a_user")


@pytest.mark.asyncio
async def test_require_login_raises_when_user_is_none():
    with pytest.raises(UnauthenticatedError):
        await _UC().execute(user=None)


@pytest.mark.asyncio
async def test_require_login_raises_when_inactive(fake_user: User):
    with pytest.raises(UserNeedsActivationError):
        await _UC().execute(user=fake_user)

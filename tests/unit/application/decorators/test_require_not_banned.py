from datetime import UTC, datetime, timedelta

import pytest

from application.decorators.auth import require_not_banned
from domain.entities.user import BanStatus, User
from domain.exceptions.auth import UserBannedError


class _UC:
    @require_not_banned
    async def execute(self, *, user: User):
        return "ok"


@pytest.mark.asyncio
async def test_require_not_banned_passes_for_clean_user(active_user: User):
    result = await _UC().execute(user=active_user)
    assert result == "ok"


@pytest.mark.asyncio
async def test_require_not_banned_raises_when_permanently_banned(active_user: User):
    active_user.ban_status = BanStatus(is_banned=True, is_permanent=True)
    with pytest.raises(UserBannedError):
        await _UC().execute(user=active_user)


@pytest.mark.asyncio
async def test_require_not_banned_raises_when_temporarily_banned(active_user: User):
    active_user.ban_status = BanStatus(
        is_banned=True,
        is_permanent=False,
        banned_till=datetime.now(UTC) + timedelta(days=1),
    )
    with pytest.raises(UserBannedError):
        await _UC().execute(user=active_user)


@pytest.mark.asyncio
async def test_require_not_banned_passes_when_temporary_ban_expired(active_user: User):
    active_user.ban_status = BanStatus(
        is_banned=True,
        is_permanent=False,
        banned_till=datetime.now(UTC) - timedelta(seconds=1),
    )
    result = await _UC().execute(user=active_user)
    assert result == "ok"

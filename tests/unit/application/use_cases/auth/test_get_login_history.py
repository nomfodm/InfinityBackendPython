from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from application.use_cases.user.get_login_history import GetLoginHistoryUseCase
from domain.entities.login_history import LoginHistoryEntry
from domain.entities.user import User
from domain.interfaces.unit_of_work import UnitOfWork


def make_entry(n: int) -> LoginHistoryEntry:
    return LoginHistoryEntry(id=n, user_id=1, timestamp=datetime.now(UTC), ip_address=f"10.0.0.{n}")


@pytest.mark.asyncio
async def test_get_login_history_success(mock_uow: UnitOfWork, active_user: User):
    entries = [make_entry(1), make_entry(2)]
    mock_uow.login_histories.get_by_user_id = AsyncMock(return_value=entries)
    uc = GetLoginHistoryUseCase(uow=mock_uow)

    result = await uc.execute(user=active_user)

    assert len(result) == 2
    assert result[0].ip_address == "10.0.0.1"
    mock_uow.login_histories.get_by_user_id.assert_awaited_once_with(user_id=active_user.id)


@pytest.mark.asyncio
async def test_get_login_history_returns_empty_list(mock_uow: UnitOfWork, active_user: User):
    mock_uow.login_histories.get_by_user_id = AsyncMock(return_value=[])
    uc = GetLoginHistoryUseCase(uow=mock_uow)

    result = await uc.execute(user=active_user)

    assert result == []

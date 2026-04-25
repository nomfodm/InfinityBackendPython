from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from application.use_cases.launcher.publish_release import (
    CreateReleaseResponse,
    PublishReleaseRequest,
    PublishReleaseUseCase,
)
from domain.entities.base import SemVer
from domain.entities.launcher import LauncherRelease
from domain.entities.user import Role, User
from domain.exceptions.auth import AccessDeniedError
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def admin_user(active_user: User) -> User:
    active_user.roles = {Role.ADMIN}
    return active_user


@pytest.fixture
def uc(mock_uow: UnitOfWork) -> PublishReleaseUseCase:
    return PublishReleaseUseCase(uow=mock_uow)


@pytest.mark.asyncio
async def test_publish_release_success(mock_uow: UnitOfWork, uc: PublishReleaseUseCase, admin_user: User):
    saved = LauncherRelease(
        id=1,
        version=SemVer("1.3.0"),
        changelog=["Исправлен краш", "Тёмная тема"],
        released_at=datetime.now(UTC),
    )
    mock_uow.launcher_releases.save = AsyncMock(return_value=saved)
    dto = PublishReleaseRequest(version=SemVer("1.3.0"), changelog=["Исправлен краш", "Тёмная тема"])

    result = await uc.execute(dto=dto, user=admin_user)

    assert isinstance(result, CreateReleaseResponse)
    assert result.id == 1
    assert result.version == "1.3.0"
    assert result.changelog == ["Исправлен краш", "Тёмная тема"]
    assert result.is_mandatory is False
    mock_uow.launcher_releases.save.assert_awaited_once()
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_publish_release_raises_for_non_admin(mock_uow: UnitOfWork, uc: PublishReleaseUseCase, active_user: User):
    dto = PublishReleaseRequest(version=SemVer("1.3.0"), changelog=["Fix"])

    with pytest.raises(AccessDeniedError):
        await uc.execute(dto=dto, user=active_user)

    mock_uow.launcher_releases.save.assert_not_called()
    mock_uow.commit.assert_not_called()

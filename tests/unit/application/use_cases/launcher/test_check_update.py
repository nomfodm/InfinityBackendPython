from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from application.use_cases.launcher.check_update import CheckUpdateRequest, CheckUpdateUseCase
from domain.entities.base import SemVer, Url
from domain.entities.launcher import LauncherRelease, LauncherReleaseAsset, Platform
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def uc(mock_uow: UnitOfWork) -> CheckUpdateUseCase:
    return CheckUpdateUseCase(uow=mock_uow)


@pytest.fixture
def release() -> LauncherRelease:
    return LauncherRelease(
        id=1,
        version=SemVer("1.3.0"),
        changelog=["Исправлен краш", "Добавлена тёмная тема"],
        released_at=datetime.now(UTC),
        assets=[
            LauncherReleaseAsset(
                platform=Platform.WINDOWS,
                download_url=Url("https://example.com/launcher-1.3.0.exe"),
                checksum="abc123",
            )
        ],
    )


@pytest.mark.asyncio
async def test_check_update_needs_update(mock_uow: UnitOfWork, uc: CheckUpdateUseCase, release: LauncherRelease):
    mock_uow.launcher_releases.get_latest_for_platform = AsyncMock(return_value=release)
    dto = CheckUpdateRequest(platform=Platform.WINDOWS, version=SemVer("1.2.0"))

    result = await uc.execute(dto=dto)

    assert result.needs_update is True
    assert result.latest is not None
    assert result.latest.version == "1.3.0"
    assert result.latest.platform == Platform.WINDOWS
    assert result.latest.checksum == "abc123"
    mock_uow.launcher_releases.get_latest_for_platform.assert_awaited_once_with(platform=Platform.WINDOWS)


@pytest.mark.asyncio
async def test_check_update_no_update_needed(mock_uow: UnitOfWork, uc: CheckUpdateUseCase, release: LauncherRelease):
    mock_uow.launcher_releases.get_latest_for_platform = AsyncMock(return_value=release)
    dto = CheckUpdateRequest(platform=Platform.WINDOWS, version=SemVer("1.3.0"))

    result = await uc.execute(dto=dto)

    assert result.needs_update is False
    assert result.latest is None


@pytest.mark.asyncio
async def test_check_update_no_release(mock_uow: UnitOfWork, uc: CheckUpdateUseCase):
    mock_uow.launcher_releases.get_latest_for_platform = AsyncMock(return_value=None)
    dto = CheckUpdateRequest(platform=Platform.WINDOWS, version=SemVer("1.0.0"))

    result = await uc.execute(dto=dto)

    assert result.needs_update is False
    assert result.latest is None

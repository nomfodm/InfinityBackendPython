from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from application.use_cases.launcher.get_latest_platform_release import (
    GetLatestPlatformReleaseRequest,
    GetLatestPlatformReleaseUseCase,
)
from domain.entities.base import SemVer, Url
from domain.entities.launcher import LauncherRelease, LauncherReleaseAsset, Platform
from domain.exceptions.launcher import LauncherReleaseNotFoundError
from domain.interfaces.unit_of_work import UnitOfWork


def _release_with_asset(platform: Platform = Platform.WINDOWS) -> LauncherRelease:
    return LauncherRelease(
        id=1,
        version=SemVer("1.0.0"),
        changelog=["Initial release"],
        released_at=datetime.now(UTC),
        is_mandatory=False,
        assets=[
            LauncherReleaseAsset(
                id=1,
                release_id=1,
                platform=platform,
                download_url=Url(f"https://cdn.example.com/launcher-{platform.value}.zip"),
                checksum="abc" * 20,
                file_size=10_000_000,
            )
        ],
    )


@pytest.mark.asyncio
async def test_get_latest_platform_release_success(mock_uow: UnitOfWork):
    release = _release_with_asset(Platform.WINDOWS)
    mock_uow.launcher_releases.get_latest_for_platform = AsyncMock(return_value=release)
    uc = GetLatestPlatformReleaseUseCase(uow=mock_uow)

    result = await uc.execute(dto=GetLatestPlatformReleaseRequest(platform=Platform.WINDOWS))

    assert result.version == "1.0.0"
    assert result.platform == Platform.WINDOWS
    assert result.file_size == 10_000_000
    assert result.checksum == "abc" * 20
    mock_uow.launcher_releases.get_latest_for_platform.assert_awaited_once_with(platform=Platform.WINDOWS)


@pytest.mark.asyncio
async def test_get_latest_platform_release_raises_when_no_release(mock_uow: UnitOfWork):
    mock_uow.launcher_releases.get_latest_for_platform = AsyncMock(return_value=None)
    uc = GetLatestPlatformReleaseUseCase(uow=mock_uow)

    with pytest.raises(LauncherReleaseNotFoundError):
        await uc.execute(dto=GetLatestPlatformReleaseRequest(platform=Platform.LINUX))

from datetime import UTC, datetime, timedelta

import pytest

from domain.entities.base import SemVer, Url
from domain.entities.launcher import LauncherRelease, LauncherReleaseAsset, Platform
from domain.exceptions.launcher import LauncherReleaseNotFoundError
from infrastructure.repositories.launcher_release_repo import SqlLauncherReleaseRepository


def make_release(version: str = "1.0.0", *, days_ago: int = 0) -> LauncherRelease:
    return LauncherRelease(
        version=SemVer(version),
        changelog=["Initial release", "Bug fixes"],
        released_at=datetime.now(UTC) - timedelta(days=days_ago),
        is_mandatory=False,
    )


def make_asset(release_id: int, platform: Platform = Platform.WINDOWS) -> LauncherReleaseAsset:
    return LauncherReleaseAsset(
        release_id=release_id,
        platform=platform,
        download_url=Url(f"https://cdn.example.com/launcher-{platform.value}.zip"),
        checksum="abc" * 20,
        file_size=123456,
    )


async def test_save_release_assigns_id(db_session):
    repo = SqlLauncherReleaseRepository(db_session)

    saved = await repo.save(make_release())

    assert saved.id is not None


async def test_save_asset_and_get_by_id_loads_assets(db_session):
    repo = SqlLauncherReleaseRepository(db_session)
    release = await repo.save(make_release("1.1.0"))
    await repo.save_launcher_release_asset(make_asset(release.id))

    found = await repo.get_by_id(release.id)

    assert found is not None
    assert len(found.assets) == 1
    assert found.assets[0].platform == Platform.WINDOWS


async def test_get_by_id_not_found(db_session):
    repo = SqlLauncherReleaseRepository(db_session)

    found = await repo.get_by_id(999_999)

    assert found is None


async def test_get_by_id_or_raise_not_found(db_session):
    repo = SqlLauncherReleaseRepository(db_session)

    with pytest.raises(LauncherReleaseNotFoundError):
        await repo.get_by_id_or_raise(999_999)


async def test_get_latest_for_platform_returns_newest(db_session):
    repo = SqlLauncherReleaseRepository(db_session)

    old = await repo.save(make_release("2.0.0", days_ago=10))
    new = await repo.save(make_release("2.1.0", days_ago=0))

    for release in (old, new):
        await repo.save_launcher_release_asset(make_asset(release.id, Platform.LINUX))

    latest = await repo.get_latest_for_platform(Platform.LINUX)

    assert latest is not None
    assert latest.version == SemVer("2.1.0")


async def test_get_latest_for_platform_only_matching_platform(db_session):
    repo = SqlLauncherReleaseRepository(db_session)
    release = await repo.save(make_release("3.0.0"))
    await repo.save_launcher_release_asset(make_asset(release.id, Platform.WINDOWS))

    found = await repo.get_latest_for_platform(Platform.MACOS)

    assert found is None


async def test_save_release_preserves_changelog(db_session):
    repo = SqlLauncherReleaseRepository(db_session)
    release = make_release("4.0.0")
    release.changelog = ["Fix crash", "Add feature", "Update deps"]

    saved = await repo.save(release)
    found = await repo.get_by_id(saved.id)

    assert found.changelog == ["Fix crash", "Add feature", "Update deps"]

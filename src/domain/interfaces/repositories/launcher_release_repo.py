from typing import Protocol

from domain.entities.launcher import LauncherRelease, LauncherReleaseAsset, Platform
from domain.exceptions.launcher import LauncherReleaseNotFoundError


class LauncherReleaseRepository(Protocol):
    async def save(self, *, release: LauncherRelease) -> LauncherRelease:
        pass

    async def get_latest_for_platform(self, *, platform: Platform) -> LauncherRelease | None:
        pass

    async def get_by_id(self, *, id: int) -> LauncherRelease | None:
        pass

    async def get_by_id_or_raise(self, *, id: int) -> LauncherRelease:
        r = await self.get_by_id(id=id)
        if r is None:
            raise LauncherReleaseNotFoundError("Версия не найдена.")
        return r

    async def save_launcher_release_asset(self, *, asset: LauncherReleaseAsset) -> LauncherReleaseAsset:
        pass

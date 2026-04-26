from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.entities.launcher import LauncherRelease, LauncherReleaseAsset, Platform
from domain.exceptions.launcher import LauncherReleaseNotFoundError
from domain.interfaces.repositories.launcher_release_repo import LauncherReleaseRepository
from infrastructure.database.models.launcher_model import LauncherReleaseAssetModel, LauncherReleaseModel


class SqlLauncherReleaseRepository(LauncherReleaseRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, release: LauncherRelease) -> LauncherRelease:
        merged = await self._session.merge(LauncherReleaseModel.from_domain(release))
        await self._session.flush()
        await self._session.refresh(merged, ["assets"])
        return merged.to_domain()

    async def get_latest_for_platform(self, platform: Platform) -> LauncherRelease | None:
        result = await self._session.execute(
            select(LauncherReleaseModel)
            .join(LauncherReleaseAssetModel)
            .where(LauncherReleaseAssetModel.platform == platform.value)
            .order_by(LauncherReleaseModel.released_at.desc())
            .limit(1)
            .options(selectinload(LauncherReleaseModel.assets))
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_id(self, id: int) -> LauncherRelease | None:
        result = await self._session.execute(
            select(LauncherReleaseModel)
            .where(LauncherReleaseModel.id == id)
            .options(selectinload(LauncherReleaseModel.assets))
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_id_or_raise(self, id: int) -> LauncherRelease:
        release = await self.get_by_id(id)
        if release is None:
            raise LauncherReleaseNotFoundError("Версия не найдена.")
        return release

    async def save_launcher_release_asset(self, asset: LauncherReleaseAsset) -> LauncherReleaseAsset:
        merged = await self._session.merge(LauncherReleaseAssetModel.from_domain(asset))
        await self._session.flush()
        return merged.to_domain()

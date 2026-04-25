from dataclasses import dataclass

from application.decorators.auth import roles_allowed
from application.dtos.common import StatusResponse
from domain.entities.base import Url
from domain.entities.launcher import LauncherReleaseAsset, Platform
from domain.entities.user import Role, User
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class AddReleaseAssetRequest:
    release_id: int
    platform: Platform
    download_url: Url
    checksum: str


class AddReleaseAssetUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @roles_allowed(Role.ADMIN)
    async def execute(self, *, dto: AddReleaseAssetRequest, user: User) -> StatusResponse:
        async with self._uow:
            await self._uow.launcher_releases.get_by_id_or_raise(id=dto.release_id)

            asset = LauncherReleaseAsset(
                platform=dto.platform, download_url=dto.download_url, release_id=dto.release_id, checksum=dto.checksum
            )

            await self._uow.launcher_releases.save_launcher_release_asset(asset=asset)

            await self._uow.commit()
            return StatusResponse()

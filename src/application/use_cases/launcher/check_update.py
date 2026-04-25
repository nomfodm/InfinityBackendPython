from dataclasses import dataclass

from application.dtos.launcher import CheckUpdateResponse, LauncherReleaseResponse
from domain.entities.base import SemVer
from domain.entities.launcher import Platform
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class CheckUpdateRequest:
    platform: Platform
    version: SemVer


class CheckUpdateUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, *, dto: CheckUpdateRequest) -> CheckUpdateResponse:
        async with self._uow:
            release = await self._uow.launcher_releases.get_latest_for_platform(platform=dto.platform)
            if release is None:
                return CheckUpdateResponse()

            needs_update = release.version > dto.version
            latest = (
                LauncherReleaseResponse.from_domain(release=release, platform=dto.platform) if needs_update else None
            )
            return CheckUpdateResponse(needs_update=needs_update, latest=latest)

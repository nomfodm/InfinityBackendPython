import datetime
from dataclasses import dataclass
from datetime import UTC

from application.decorators.auth import roles_allowed
from domain.entities.base import SemVer
from domain.entities.launcher import LauncherRelease
from domain.entities.user import Role, User
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class PublishReleaseRequest:
    version: SemVer
    changelog: list[str]
    is_mandatory: bool = False


@dataclass(frozen=True)
class CreateReleaseResponse:
    id: int
    version: str
    changelog: list[str]
    is_mandatory: bool
    released_at: datetime.datetime

    @classmethod
    def from_domain(cls, release: LauncherRelease):
        return cls(
            id=release.id,
            version=release.version.value,
            changelog=release.changelog,
            is_mandatory=release.is_mandatory,
            released_at=release.released_at,
        )


class PublishReleaseUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @roles_allowed(Role.ADMIN)
    async def execute(self, *, dto: PublishReleaseRequest, user: User) -> CreateReleaseResponse:
        async with self._uow:
            release = LauncherRelease(
                released_at=datetime.datetime.now(UTC),
                changelog=dto.changelog,
                version=dto.version,
                is_mandatory=dto.is_mandatory,
            )

            saved = await self._uow.launcher_releases.save(release=release)

            await self._uow.commit()
            return CreateReleaseResponse.from_domain(saved)

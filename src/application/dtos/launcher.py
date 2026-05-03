from dataclasses import dataclass
from datetime import datetime

from domain.entities.launcher import LauncherRelease, Platform


@dataclass(frozen=True)
class LauncherReleaseResponse:
    id: int | None
    version: str
    platform: str
    download_url: str
    checksum: str
    file_size: int
    changelog: list[str]
    released_at: datetime
    is_mandatory: bool

    @classmethod
    def from_domain(cls, *, release: LauncherRelease, platform: Platform):
        asset = next(a for a in release.assets if a.platform == platform)
        return cls(
            id=release.id,
            version=release.version.value,
            platform=platform,
            download_url=asset.download_url.value,
            checksum=asset.checksum,
            file_size=asset.file_size,
            changelog=release.changelog,
            released_at=release.released_at,
            is_mandatory=release.is_mandatory,
        )


@dataclass(frozen=True)
class CheckUpdateResponse:
    needs_update: bool = False
    latest: LauncherReleaseResponse | None = None

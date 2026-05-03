from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from domain.entities.base import SemVer, Url


class Platform(StrEnum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


@dataclass
class LauncherReleaseAsset:
    platform: Platform
    download_url: Url
    checksum: str  # SHA256
    file_size: int
    release_id: int | None = None
    id: int | None = None


@dataclass
class LauncherRelease:
    version: SemVer
    changelog: list[str]
    released_at: datetime
    is_mandatory: bool = False
    assets: list[LauncherReleaseAsset] = field(default_factory=list)
    id: int | None = None

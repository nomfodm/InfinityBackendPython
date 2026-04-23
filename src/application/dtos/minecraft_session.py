from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ProfileProperty:
    name: str
    value: str
    signature: str | None = None


@dataclass(frozen=True)
class ProfileResponse:
    id: str
    name: str
    properties: list[ProfileProperty]


@dataclass(frozen=True)
class MinecraftSessionResponse:
    access_token: str
    profile_uuid: str
    nickname: str

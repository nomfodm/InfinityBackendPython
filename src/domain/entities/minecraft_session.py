from dataclasses import dataclass
from uuid import UUID

from domain.entities.base import UserRelatedHandle, MCAccessToken, MCServerID


@dataclass
class MinecraftSession:
    access_token: MCAccessToken
    nickname: UserRelatedHandle
    profile_uuid: UUID  # Unique constraint
    user_id: int
    server_id: MCServerID | None = None

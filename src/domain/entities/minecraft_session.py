from dataclasses import dataclass
from uuid import UUID

from domain.entities.base import MCAccessToken, MCServerID, UserRelatedHandle


@dataclass
class MinecraftSession:
    access_token: MCAccessToken
    nickname: UserRelatedHandle
    profile_uuid: UUID  # Unique constraint
    user_id: int
    server_id: MCServerID | None = None

from dataclasses import dataclass
from uuid import UUID

from domain.entities.base import UserRelatedHandle


@dataclass
class MinecraftProfile:
    user_id: int
    uuid: UUID  # Unique constraint
    nickname: UserRelatedHandle  # Unique constraint

    active_skin_id: int | None = None
    active_cape_id: int | None = None

    id: int | None = None

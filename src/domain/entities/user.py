from dataclasses import dataclass, field
import datetime
import enum

from domain.entities.base import UserRelatedHandle, Email


class Role(str, enum.Enum):
    PLAYER = "player"
    ADMIN = "admin"


@dataclass
class BanStatus:
    is_banned: bool = False
    is_permanent: bool = False
    banned_till: datetime.datetime | None = None

@dataclass
class User:
    email: Email  # Unique constraint
    username: UserRelatedHandle  # Unique constraint
    password_hash: str

    registered_at: datetime.datetime

    roles: set[Role] = field(default_factory=lambda: {Role.PLAYER})

    ban_status: BanStatus = field(default_factory=lambda: BanStatus())
    is_active: bool = False

    id: int | None = None


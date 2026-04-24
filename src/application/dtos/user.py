import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class BanStatusResponse:
    is_banned: bool
    is_permanent: bool
    banned_till: datetime.datetime | None
    admin_user_id: int | None = None

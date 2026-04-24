import datetime
from dataclasses import dataclass


@dataclass
class LoginHistoryEntry:
    user_id: int
    timestamp: datetime.datetime
    ip_address: str | None = None
    user_agent: str | None = None
    id: int | None = None

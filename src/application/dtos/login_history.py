import datetime
from dataclasses import dataclass

from domain.entities.login_history import LoginHistoryEntry


@dataclass(frozen=True)
class LoginHistoryEntryResponse:
    id: int | None
    timestamp: datetime.datetime
    ip_address: str | None
    user_agent: str | None

    @classmethod
    def from_domain(cls, entry: LoginHistoryEntry):
        return cls(
            id=entry.id,
            timestamp=entry.timestamp,
            ip_address=entry.ip_address,
            user_agent=entry.user_agent,
        )

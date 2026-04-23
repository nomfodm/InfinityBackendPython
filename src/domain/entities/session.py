from dataclasses import dataclass
import datetime
import uuid


@dataclass
class Session:
    user_id: int
    refresh_token_hash: str
    expires_at: datetime.datetime
    is_revoked: bool = False

    created_at: datetime.datetime | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    last_used_at: datetime.datetime | None = None
    id: uuid.UUID | None = None
    

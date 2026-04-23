from dataclasses import dataclass
import datetime
import uuid


@dataclass
class Session:
    user_id: int
    refresh_token_hash: str
    expires_at: datetime.datetime
    is_revoked: bool = False

    last_used_at: datetime.datetime | None = None
    id: uuid.UUID | None = None
    

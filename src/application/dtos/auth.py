import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPairResponse:
    access_token: str
    refresh_split_token: str


@dataclass(frozen=True)
class SessionCredentials:
    id: uuid.UUID
    refresh_token: str

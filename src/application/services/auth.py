import datetime
import uuid
from dataclasses import dataclass
from datetime import UTC, timedelta

from application.constants import ACCESS_TOKEN_EXPIRES_MINUTES, REFRESH_TOKEN_EXPIRES_DAYS
from application.dtos.auth import TokenPairResponse
from domain.entities.session import Session
from domain.exceptions.session import SessionRevokedError, SessionExpiredError, TokenAuthenticityError, \
    SessionNotFoundError
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.services.token_service import TokenService


@dataclass(frozen=True)
class SessionTokensDTO:
    tokens: TokenPairResponse
    session: Session


class AuthService:
    def __init__(self, *,
                 token_hasher: StringHasher,
                 token_service: TokenService):
        self._token_hasher = token_hasher
        self._token_service = token_service

    def create_session_and_tokens(self, *, user_id: int) -> SessionTokensDTO:
        access_token = self.generate_access_token(user_id=user_id)
        refresh_token, refresh_token_expires_at, refresh_token_hash = self.generate_refresh_token()

        new_session = Session(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=refresh_token_expires_at,
            id=uuid.uuid4()
        )

        return SessionTokensDTO(
            tokens=TokenPairResponse(
                access_token=access_token,
                refresh_split_token=f"{new_session.id}.{refresh_token}"
            ),
            session=new_session
        )

    def verify_session(self, *, refresh_token: str, session: Session | None):
        if session is None:
            raise SessionNotFoundError("Сессия не найдена.")

        if session.is_revoked:
            raise SessionRevokedError("Эта сессия была закрыта.")

        if session.expires_at <= datetime.datetime.now(UTC):
            raise SessionExpiredError("Сессия истекла.")

        if not self._token_hasher.verify(raw=refresh_token, hashed=session.refresh_token_hash):
            raise TokenAuthenticityError("Попытка подмены токена.")

    def generate_access_token(self, *, user_id: int) -> str:
        access_token = self._token_service.generate_access_token(
            data={"sub": str(user_id)},
            expires_in_minutes=ACCESS_TOKEN_EXPIRES_MINUTES
        )
        return access_token

    def generate_refresh_token(self) -> tuple[str, datetime.datetime, str]:
        refresh_token = self._token_service.generate_refresh_token()
        refresh_token_expires_at = datetime.datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS)
        return refresh_token, refresh_token_expires_at, self._token_hasher.hash(raw=refresh_token)

import datetime
import secrets
from datetime import UTC

import jwt

from domain.exceptions.session import TokenAuthenticityError
from domain.interfaces.services.token_service import TokenService


class JWTTokenService(TokenService):
    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm

    def generate_access_token(self, data: dict, expires_in_minutes: int) -> str:
        payload = data | {"exp": datetime.datetime.now(UTC) + datetime.timedelta(minutes=expires_in_minutes)}
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def generate_refresh_token(self) -> str:
        return secrets.token_urlsafe(64)

    def decode_access_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.PyJWTError as e:
            raise TokenAuthenticityError(str(e)) from e

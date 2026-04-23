from typing import Protocol


class TokenService(Protocol):
    def generate_access_token(self, *, data: dict, expires_in_minutes: int) -> str:
        pass

    def generate_refresh_token(self) -> str:
        pass

    def decode_access_token(self, *, token: str) -> dict:
        pass

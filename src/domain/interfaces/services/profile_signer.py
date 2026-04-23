from typing import Protocol


class ProfileSigner(Protocol):
    def sign(self, payload: str) -> str:
        pass

    def get_public_key(self) -> str:
        pass

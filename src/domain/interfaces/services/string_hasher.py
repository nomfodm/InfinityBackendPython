from typing import Protocol


class StringHasher(Protocol):
    def hash(self, *, raw: str) -> str:
        pass

    def verify(self, *, raw: str, hashed: str) -> bool:
        pass
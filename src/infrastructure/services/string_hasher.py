import bcrypt

from domain.interfaces.services.string_hasher import StringHasher


class BcryptStringHasher(StringHasher):
    def hash(self, raw: str) -> str:
        return bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

    def verify(self, raw: str, hashed: str) -> bool:
        return bcrypt.checkpw(raw.encode(), hashed.encode())

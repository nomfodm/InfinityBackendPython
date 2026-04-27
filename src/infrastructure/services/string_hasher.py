import base64
import hashlib

import bcrypt

from domain.interfaces.services.string_hasher import StringHasher


class BcryptStringHasher(StringHasher):
    @staticmethod
    def _prepare(raw: str) -> bytes:
        # bcrypt truncates at 72 bytes; pre-hash with SHA-256 to handle arbitrary lengths
        digest = hashlib.sha256(raw.encode()).digest()
        return base64.b64encode(digest)

    def hash(self, raw: str) -> str:
        return bcrypt.hashpw(self._prepare(raw), bcrypt.gensalt()).decode()

    def verify(self, raw: str, hashed: str) -> bool:
        return bcrypt.checkpw(self._prepare(raw), hashed.encode())

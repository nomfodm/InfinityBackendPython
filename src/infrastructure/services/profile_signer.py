import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from domain.interfaces.services.profile_signer import ProfileSigner


class RSAProfileSigner(ProfileSigner):
    def __init__(self, *, private_key_pem: str) -> None:
        self._private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
        )

    def sign(self, payload: str) -> str:
        signature = self._private_key.sign(
            payload.encode(),
            padding.PKCS1v15(),
            hashes.SHA1(),  # noqa: S303 — Yggdrasil requires SHA1withRSA
        )
        return base64.b64encode(signature).decode()

    def get_public_key(self) -> str:
        der = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return base64.b64encode(der).decode()

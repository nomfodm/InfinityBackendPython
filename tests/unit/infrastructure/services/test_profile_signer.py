import base64

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from infrastructure.services.profile_signer import RSAProfileSigner


@pytest.fixture(scope="module")
def private_key_pem() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


@pytest.fixture(scope="module")
def signer(private_key_pem) -> RSAProfileSigner:
    return RSAProfileSigner(private_key_pem=private_key_pem)


def test_sign_returns_base64_string(signer):
    result = signer.sign('{"id":"abc","name":"player"}')

    base64.b64decode(result)  # должно не падать


def test_signature_verifiable_with_public_key(signer, private_key_pem):
    payload = '{"id":"abc","name":"player"}'
    signature = base64.b64decode(signer.sign(payload))

    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    public_key = private_key.public_key()

    public_key.verify(signature, payload.encode(), padding.PKCS1v15(), hashes.SHA1())  # не должно бросать


def test_different_payloads_different_signatures(signer):
    sig1 = signer.sign("payload_one")
    sig2 = signer.sign("payload_two")

    assert sig1 != sig2


def test_get_public_key_returns_base64_der(signer):
    result = signer.get_public_key()

    der = base64.b64decode(result)
    # DER-закодированный SubjectPublicKeyInfo начинается с 0x30 (SEQUENCE)
    assert der[0] == 0x30


def test_get_public_key_consistent(signer):
    assert signer.get_public_key() == signer.get_public_key()

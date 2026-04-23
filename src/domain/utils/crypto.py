import hashlib
import secrets


def sha256(data: bytes) -> str:
    if not data:
        raise ValueError("Невозможно рассчитать хэш, данные отсутствуют")
    return hashlib.sha256(data).hexdigest()


def generate_token_32_length():
    return secrets.token_hex(16)

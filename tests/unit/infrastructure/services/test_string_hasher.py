from infrastructure.services.string_hasher import BcryptStringHasher


def test_hash_returns_different_string():
    hasher = BcryptStringHasher()

    result = hasher.hash("secret")

    assert result != "secret"


def test_hash_same_input_different_output():
    hasher = BcryptStringHasher()

    h1 = hasher.hash("secret")
    h2 = hasher.hash("secret")

    assert h1 != h2  # bcrypt uses random salt


def test_verify_correct_password():
    hasher = BcryptStringHasher()
    hashed = hasher.hash("mypassword")

    assert hasher.verify("mypassword", hashed) is True


def test_verify_wrong_password():
    hasher = BcryptStringHasher()
    hashed = hasher.hash("mypassword")

    assert hasher.verify("wrongpassword", hashed) is False


def test_verify_empty_password():
    hasher = BcryptStringHasher()
    hashed = hasher.hash("")

    assert hasher.verify("", hashed) is True
    assert hasher.verify(" ", hashed) is False

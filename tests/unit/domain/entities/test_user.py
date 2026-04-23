import pytest

from domain.entities.base import UserRelatedHandle, Email
from domain.exceptions.base import ValidationError


def test_email_validation_success():
    email = Email("coolmail@infinity.ru")
    assert str(email) == "coolmail@infinity.ru"


def test_email_validation_fails():
    with pytest.raises(ValidationError):
        Email("coolmailinfinity.ru")
    with pytest.raises(ValidationError):
        Email("coolfgfd1")
    with pytest.raises(ValidationError):
        Email("coolfgfd1@fsdfsdf")


def test_username_validation_success():
    username = UserRelatedHandle("infinity")
    assert str(username) == "infinity"

def test_username_validation_fails():
    with pytest.raises(ValidationError):
        UserRelatedHandle("fdf")
    with pytest.raises(ValidationError):
        UserRelatedHandle("fdffsdfsdfsdfsdfsdfsdfsdsd")
    with pytest.raises(ValidationError):
        UserRelatedHandle("fd233-4sd")


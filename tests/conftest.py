import uuid
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from pytest_mock import MockerFixture

from domain.entities.base import Email, UserRelatedHandle
from domain.entities.session import Session
from domain.entities.user import User
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.fixture
def mock_uow(mocker: MockerFixture) -> UnitOfWork:
    uow = mocker.MagicMock()

    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None

    uow.users = mocker.AsyncMock()
    uow.verification_codes = mocker.AsyncMock()
    uow.minecraft_profiles = mocker.AsyncMock()
    uow.sessions = mocker.AsyncMock()
    uow.minecraft_sessions = mocker.AsyncMock()
    uow.wardrobe = mocker.AsyncMock()
    uow.textures = mocker.AsyncMock()
    uow.texture_catalog = mocker.AsyncMock()

    uow.login_histories = mocker.AsyncMock()
    uow.launcher_releases = mocker.AsyncMock()

    uow.commit = mocker.AsyncMock()
    uow.rollback = mocker.AsyncMock()

    return cast(UnitOfWork, uow)


@pytest.fixture
def fake_session():
    return Session(
        id=uuid.uuid4(),
        user_id=1,
        is_revoked=False,
        expires_at=datetime.now(UTC) + timedelta(days=1),
        refresh_token_hash="refresh_token_hash",
    )


@pytest.fixture
def fake_user():
    return User(
        id=1,
        email=Email("test@test.com"),
        username=UserRelatedHandle("tester"),
        password_hash="hash",
        registered_at=datetime.now(UTC),
    )


@pytest.fixture
def active_user(fake_user: User) -> User:
    fake_user.is_active = True
    return fake_user

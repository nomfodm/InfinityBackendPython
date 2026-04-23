import datetime
from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from application.dtos.auth import TokenPairResponse
from application.services.auth import AuthService


@pytest.fixture
def mock_auth_service(mocker: MockerFixture) -> AuthService:
    mock_auth_service_class = mocker.patch("application.use_cases.auth.register_user_and_login.AuthService")

    mock_auth_instance = mock_auth_service_class.return_value
    fake_session_tokens = MagicMock()
    fake_session_tokens.tokens = TokenPairResponse(
        access_token="access_token", refresh_split_token="uuid.refresh_token"
    )
    mock_auth_instance.create_session_and_tokens.return_value = fake_session_tokens
    mock_auth_instance.generate_access_token.return_value = "access_token"
    mock_auth_instance.generate_refresh_token.return_value = (
        "refresh_token",
        datetime.datetime.now(datetime.UTC),
        "refresh_token_hash",
    )

    return cast(AuthService, mock_auth_instance)

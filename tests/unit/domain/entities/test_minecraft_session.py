import pytest
import uuid

from domain.entities.minecraft_session import MinecraftSession
from domain.entities.base import MCAccessToken, MCServerID, UserRelatedHandle
from domain.exceptions.base import ValidationError


def test_minecraft_session_validation_success():
    MinecraftSession(
        access_token=MCAccessToken("q" * 32),
        server_id=MCServerID("q" * 32),
        nickname=UserRelatedHandle("player123"),
        profile_uuid=uuid.uuid4(),
        user_id=1
    )
    MinecraftSession(
        access_token=MCAccessToken("q" * 32),
        server_id=MCServerID("q" * 33),
        nickname=UserRelatedHandle("player123"),
        profile_uuid=uuid.uuid4(),
        user_id=1
    )


def test_minecraft_session_validation_fails():
    with pytest.raises(ValidationError):
        MinecraftSession(
            access_token=MCAccessToken("q" * 40),
            server_id=MCServerID("q" * 32),
            nickname=UserRelatedHandle("player123"),
            profile_uuid=uuid.uuid4(),
            user_id=1
        )
    with pytest.raises(ValidationError):
        MinecraftSession(
            access_token=MCAccessToken("q" * 32),
            server_id=MCServerID("q" * 40),
            nickname=UserRelatedHandle("player123"),
            profile_uuid=uuid.uuid4(),
            user_id=1
        )

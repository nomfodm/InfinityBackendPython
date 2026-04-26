from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.constants import MC_SESSION_TTL_SECONDS
from application.dtos.minecraft_session import ProfileResponse
from application.use_cases.launcher.minecraft_session.create_minecraft_session import CreateMinecraftSessionUseCase
from application.use_cases.launcher.minecraft_session.has_joined_server import HasJoinedRequest, HasJoinedServerUseCase
from application.use_cases.launcher.minecraft_session.join_server import JoinServerRequest, JoinServerUseCase
from application.use_cases.launcher.minecraft_session.profile import ProfileRequest, ProfileUseCase
from domain.entities.base import MCAccessToken, MCServerID, UserRelatedHandle
from domain.entities.minecraft_session import MinecraftSession
from domain.entities.user import User
from domain.exceptions.minecraft import InvalidMCAccessToken, InvalidMCServerID
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.mark.asyncio
async def test_create_minecraft_session_success(mock_uow: UnitOfWork, active_user: User):
    profile_uuid = uuid4()
    mc_profile = SimpleNamespace(uuid=profile_uuid, nickname=UserRelatedHandle("tester"), user_id=active_user.id)
    saved_session = MinecraftSession(
        user_id=active_user.id,
        profile_uuid=profile_uuid,
        nickname=UserRelatedHandle("tester"),
        access_token=MCAccessToken("a" * 32),
    )
    mock_uow.minecraft_profiles.get_by_user_id_or_raise = AsyncMock(return_value=mc_profile)
    mock_uow.minecraft_sessions.save = AsyncMock(return_value=saved_session)

    result = await CreateMinecraftSessionUseCase(uow=mock_uow).execute(user=active_user)

    assert result.access_token == "a" * 32
    assert result.profile_uuid == str(profile_uuid)
    mock_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_join_server_fails_on_invalid_access_token(mock_uow: UnitOfWork):
    profile_uuid = uuid4()
    session = MinecraftSession(
        user_id=1,
        profile_uuid=profile_uuid,
        nickname=UserRelatedHandle("tester"),
        access_token=MCAccessToken("a" * 32),
    )
    mock_uow.minecraft_sessions.get_by_profile_uuid_or_raise = AsyncMock(return_value=session)
    uc = JoinServerUseCase(uow=mock_uow)

    with pytest.raises(InvalidMCAccessToken):
        await uc.execute(
            dto=JoinServerRequest(
                access_token=MCAccessToken("b" * 32),
                selected_profile=profile_uuid,
                server_id=MCServerID("s" * 32),
            )
        )

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_has_joined_fails_on_wrong_server_id(mock_uow: UnitOfWork, mocker):
    mc_profile = SimpleNamespace(
        uuid=uuid4(),
        user_id=1,
        active_skin_id=None,
        active_cape_id=None,
        nickname=UserRelatedHandle("tester"),
    )
    mc_session = SimpleNamespace(server_id=MCServerID("a" * 32))
    mock_uow.minecraft_profiles.get_by_nickname_or_raise = AsyncMock(return_value=mc_profile)
    mock_uow.minecraft_sessions.get_by_profile_uuid_or_raise = AsyncMock(return_value=mc_session)
    uc = HasJoinedServerUseCase(uow=mock_uow, mc_profile_service=mocker.MagicMock())

    with pytest.raises(InvalidMCServerID):
        await uc.execute(dto=HasJoinedRequest(username=UserRelatedHandle("tester"), server_id=MCServerID("b" * 32)))


@pytest.mark.asyncio
async def test_profile_use_case_builds_response(mock_uow: UnitOfWork, mocker):
    mc_profile = SimpleNamespace(
        uuid=uuid4(),
        user_id=1,
        active_skin_id=None,
        active_cape_id=None,
    )
    expected = ProfileResponse(id="1", name="tester", properties=[])
    profile_service = mocker.MagicMock()
    profile_service.build_profile_response.return_value = expected
    mock_uow.minecraft_profiles.get_by_uuid_or_raise = AsyncMock(return_value=mc_profile)

    result = await ProfileUseCase(uow=mock_uow, mc_profile_service=profile_service).execute(
        dto=ProfileRequest(uuid=mc_profile.uuid)
    )

    assert result == expected


@pytest.mark.asyncio
async def test_join_server_success(mock_uow: UnitOfWork):
    profile_uuid = uuid4()
    server_id = MCServerID("s" * 32)
    session = MinecraftSession(
        user_id=1,
        profile_uuid=profile_uuid,
        nickname=UserRelatedHandle("tester"),
        access_token=MCAccessToken("a" * 32),
    )
    mock_uow.minecraft_sessions.get_by_profile_uuid_or_raise = AsyncMock(return_value=session)
    uc = JoinServerUseCase(uow=mock_uow)

    result = await uc.execute(
        dto=JoinServerRequest(
            access_token=MCAccessToken("a" * 32),
            selected_profile=profile_uuid,
            server_id=server_id,
        )
    )

    assert result.ok is True
    assert session.server_id == server_id
    mock_uow.minecraft_sessions.save.assert_awaited_once_with(mc_session=session, ttl=MC_SESSION_TTL_SECONDS)
    mock_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_has_joined_success(mock_uow: UnitOfWork, mocker):
    profile_uuid = uuid4()
    server_id = MCServerID("a" * 32)
    mc_profile = SimpleNamespace(
        uuid=profile_uuid,
        user_id=1,
        active_skin_id=None,
        active_cape_id=None,
        nickname=UserRelatedHandle("tester"),
    )
    mc_session = SimpleNamespace(server_id=server_id)
    expected = ProfileResponse(id=str(profile_uuid), name="tester", properties=[])
    mock_uow.minecraft_profiles.get_by_nickname_or_raise = AsyncMock(return_value=mc_profile)
    mock_uow.minecraft_sessions.get_by_profile_uuid_or_raise = AsyncMock(return_value=mc_session)
    profile_service = mocker.MagicMock()
    profile_service.build_profile_response.return_value = expected

    result = await HasJoinedServerUseCase(uow=mock_uow, mc_profile_service=profile_service).execute(
        dto=HasJoinedRequest(username=UserRelatedHandle("tester"), server_id=server_id)
    )

    assert result == expected
    profile_service.build_profile_response.assert_called_once()

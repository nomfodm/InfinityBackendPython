from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from application.constants import VERIFICATION_CODE_TTL_SECONDS
from application.use_cases.auth.reset_password import ResetPasswordRequest, ResetPasswordUseCase
from application.use_cases.user.activate_user import ActivateUserRequest, ActivateUserUseCase
from application.use_cases.user.change_email import ChangeEmailRequest, ChangeEmailUseCase
from application.use_cases.user.change_password import ChangePasswordRequest, ChangePasswordUseCase
from application.use_cases.user.change_username import ChangeUsernameRequest, ChangeUsernameUseCase
from application.use_cases.user.me import MeUseCase
from application.use_cases.user.minecraft_profile.change_nickname import ChangeNicknameRequest, ChangeNicknameUseCase
from application.use_cases.user.send_verification_code import SendVerificationCodeRequest, SendVerificationCodeUseCase
from domain.entities.base import ContentLabel, Email, Url, UserRelatedHandle
from domain.entities.user import BanStatus, User
from domain.entities.verification_code import VerificationCodePurpose
from domain.entities.wardrobe import Texture, TextureType, WardrobeItem
from domain.exceptions.auth import EmailTakenError, InvalidCredentialError, UsernameTakenError
from domain.exceptions.user import InvalidVerificationCode, NicknameTakenError
from domain.interfaces.services.code_generator import CodeGenerator
from domain.interfaces.services.email_service import EmailService
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork


@pytest.mark.asyncio
async def test_send_verification_code_success(mock_uow: UnitOfWork, active_user: User, mocker):
    code_generator = mocker.MagicMock(spec=CodeGenerator)
    code_generator.generate.return_value = "123456"
    email_service = mocker.AsyncMock(spec=EmailService)
    uc = SendVerificationCodeUseCase(uow=mock_uow, email_service=email_service, code_generator=code_generator)

    dto = SendVerificationCodeRequest(purpose=VerificationCodePurpose.ACTIVATION)
    result = await uc.execute(dto=dto, user=active_user)

    mock_uow.verification_codes.save_code.assert_awaited_once_with(
        email=active_user.email,
        purpose=VerificationCodePurpose.ACTIVATION,
        code="123456",
        ttl=VERIFICATION_CODE_TTL_SECONDS,
    )
    email_service.send_verification_code.assert_awaited_once_with(email=active_user.email, code="123456")
    assert result.email == active_user.email.value
    assert result.expires_at.tzinfo is UTC


@pytest.mark.asyncio
async def test_activate_user_fails_when_code_missing(mock_uow: UnitOfWork):
    mock_uow.verification_codes.get_code = AsyncMock(return_value=None)
    uc = ActivateUserUseCase(uow=mock_uow)
    dto = ActivateUserRequest(email=Email("player@example.com"), verification_code="123456")

    with pytest.raises(InvalidVerificationCode):
        await uc.execute(dto=dto)

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_activate_user_success_sets_active_and_saves(mock_uow: UnitOfWork, fake_user: User):
    mock_uow.verification_codes.get_code = AsyncMock(return_value="123456")
    mock_uow.users.get_by_email = AsyncMock(return_value=fake_user)
    uc = ActivateUserUseCase(uow=mock_uow)
    dto = ActivateUserRequest(email=Email("player@example.com"), verification_code="123456")

    result = await uc.execute(dto=dto)

    assert result.ok is True
    assert fake_user.is_active is True
    mock_uow.users.save.assert_awaited_once_with(user=fake_user)
    mock_uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_activate_user_fails_when_code_wrong(mock_uow: UnitOfWork):
    mock_uow.verification_codes.get_code = AsyncMock(return_value="999999")
    uc = ActivateUserUseCase(uow=mock_uow)
    dto = ActivateUserRequest(email=Email("player@example.com"), verification_code="123456")

    with pytest.raises(InvalidVerificationCode):
        await uc.execute(dto=dto)

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_change_email_fails_when_taken_by_other(mock_uow: UnitOfWork, active_user: User):
    mock_uow.users.get_by_email = AsyncMock(return_value=SimpleNamespace(id=999))
    uc = ChangeEmailUseCase(uow=mock_uow)

    with pytest.raises(EmailTakenError):
        await uc.execute(dto=ChangeEmailRequest(new_email=Email("new@example.com")), user=active_user)

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_change_email_success_deactivates_user(mock_uow: UnitOfWork, active_user: User):
    mock_uow.users.get_by_email = AsyncMock(return_value=None)
    uc = ChangeEmailUseCase(uow=mock_uow)

    result = await uc.execute(dto=ChangeEmailRequest(new_email=Email("new@example.com")), user=active_user)

    assert result.ok is True
    assert active_user.email.value == "new@example.com"
    assert active_user.is_active is False
    mock_uow.users.save.assert_awaited_once_with(user=active_user)


@pytest.mark.asyncio
async def test_change_email_success_when_email_is_own(mock_uow: UnitOfWork, active_user: User):
    mock_uow.users.get_by_email = AsyncMock(return_value=active_user)
    uc = ChangeEmailUseCase(uow=mock_uow)

    result = await uc.execute(dto=ChangeEmailRequest(new_email=Email("new@example.com")), user=active_user)

    assert result.ok is True
    mock_uow.users.save.assert_awaited_once_with(user=active_user)


@pytest.mark.asyncio
async def test_change_password_fails_on_invalid_old_password(mock_uow: UnitOfWork, active_user: User, mocker):
    hasher = mocker.MagicMock(spec=StringHasher)
    hasher.verify.return_value = False
    uc = ChangePasswordUseCase(uow=mock_uow, hasher=hasher)

    with pytest.raises(InvalidCredentialError):
        await uc.execute(dto=ChangePasswordRequest(old_password="bad", new_password="new"), user=active_user)

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_change_password_success_hashes_and_saves(mock_uow: UnitOfWork, active_user: User, mocker):
    hasher = mocker.MagicMock(spec=StringHasher)
    hasher.verify.return_value = True
    hasher.hash.return_value = "new_hash"
    uc = ChangePasswordUseCase(uow=mock_uow, hasher=hasher)

    result = await uc.execute(dto=ChangePasswordRequest(old_password="old", new_password="new"), user=active_user)

    assert result.ok is True
    assert active_user.password_hash == "new_hash"
    hasher.hash.assert_called_once_with(raw="new")
    mock_uow.users.save.assert_awaited_once_with(user=active_user)


@pytest.mark.asyncio
async def test_change_username_fails_if_taken(mock_uow: UnitOfWork, active_user: User):
    mock_uow.users.get_by_username = AsyncMock(return_value=SimpleNamespace(id=777))
    uc = ChangeUsernameUseCase(uow=mock_uow)

    with pytest.raises(UsernameTakenError):
        await uc.execute(dto=ChangeUsernameRequest(new_username=UserRelatedHandle("newname")), user=active_user)


@pytest.mark.asyncio
async def test_change_username_success(mock_uow: UnitOfWork, active_user: User):
    mock_uow.users.get_by_username = AsyncMock(return_value=None)
    uc = ChangeUsernameUseCase(uow=mock_uow)

    result = await uc.execute(dto=ChangeUsernameRequest(new_username=UserRelatedHandle("newname")), user=active_user)

    assert result.ok is True
    assert active_user.username.value == "newname"
    mock_uow.users.save.assert_awaited_once_with(user=active_user)


@pytest.mark.asyncio
async def test_change_username_success_when_username_is_own(mock_uow: UnitOfWork, active_user: User):
    mock_uow.users.get_by_username = AsyncMock(return_value=active_user)
    uc = ChangeUsernameUseCase(uow=mock_uow)

    result = await uc.execute(dto=ChangeUsernameRequest(new_username=UserRelatedHandle("tester")), user=active_user)

    assert result.ok is True
    mock_uow.users.save.assert_awaited_once_with(user=active_user)


@pytest.mark.asyncio
async def test_change_nickname_fails_if_taken_by_other(mock_uow: UnitOfWork, active_user: User):
    mock_uow.minecraft_profiles.get_by_nickname = AsyncMock(return_value=SimpleNamespace(user_id=2))
    uc = ChangeNicknameUseCase(uow=mock_uow)

    with pytest.raises(NicknameTakenError):
        await uc.execute(dto=ChangeNicknameRequest(new_nickname=UserRelatedHandle("newname")), user=active_user)


@pytest.mark.asyncio
async def test_change_nickname_success(mock_uow: UnitOfWork, active_user: User):
    mc_profile = SimpleNamespace(user_id=active_user.id, nickname=UserRelatedHandle("oldname"))
    mock_uow.minecraft_profiles.get_by_nickname = AsyncMock(return_value=None)
    mock_uow.minecraft_profiles.get_by_user_id_or_raise = AsyncMock(return_value=mc_profile)
    uc = ChangeNicknameUseCase(uow=mock_uow)

    result = await uc.execute(dto=ChangeNicknameRequest(new_nickname=UserRelatedHandle("newname")), user=active_user)

    assert result.ok is True
    assert mc_profile.nickname == UserRelatedHandle("newname")
    mock_uow.minecraft_profiles.save.assert_awaited_once_with(profile=mc_profile)


@pytest.mark.asyncio
async def test_change_nickname_success_when_nickname_is_own(mock_uow: UnitOfWork, active_user: User):
    mc_profile = SimpleNamespace(user_id=active_user.id, nickname=UserRelatedHandle("tester"))
    mock_uow.minecraft_profiles.get_by_nickname = AsyncMock(return_value=mc_profile)
    mock_uow.minecraft_profiles.get_by_user_id_or_raise = AsyncMock(return_value=mc_profile)
    uc = ChangeNicknameUseCase(uow=mock_uow)

    result = await uc.execute(dto=ChangeNicknameRequest(new_nickname=UserRelatedHandle("tester")), user=active_user)

    assert result.ok is True
    mock_uow.minecraft_profiles.save.assert_awaited_once_with(profile=mc_profile)


@pytest.mark.asyncio
async def test_me_use_case_maps_response_dto(mock_uow: UnitOfWork, active_user: User):
    active_user.ban_status = BanStatus(is_banned=False)
    active_user.roles = set(active_user.roles)
    mc_profile = SimpleNamespace(
        id=5,
        user_id=active_user.id,
        uuid=uuid4(),
        nickname=UserRelatedHandle("tester"),
        active_skin_id=10,
        active_cape_id=None,
    )
    texture = Texture(hash="ab" * 32, type=TextureType.SKIN, url=Url("https://example.com/skins/a.png"))
    wardrobe_item = WardrobeItem(
        id=10,
        user_id=active_user.id,
        author_id=active_user.id,
        texture=texture,
        acquired_at=datetime.now(UTC),
        label=ContentLabel("Nice skin"),
    )
    mock_uow.minecraft_profiles.get_by_user_id_or_raise = AsyncMock(return_value=mc_profile)
    mock_uow.wardrobe.get_user_wardrobe = AsyncMock(return_value=[wardrobe_item])
    mock_uow.wardrobe.get_by_id_from_user_wardrobe_or_raise = AsyncMock(return_value=wardrobe_item)

    result = await MeUseCase(uow=mock_uow).execute(user=active_user)

    assert result.email == active_user.email.value
    assert isinstance(result.roles, list)
    assert result.minecraft_profile.active_skin is not None
    assert result.minecraft_profile.active_skin.texture.type == "skin"


@pytest.mark.asyncio
async def test_reset_password_fails_when_code_missing(mock_uow: UnitOfWork, mocker):
    mock_uow.verification_codes.get_code = AsyncMock(return_value=None)
    hasher = mocker.MagicMock(spec=StringHasher)
    uc = ResetPasswordUseCase(uow=mock_uow, hasher=hasher)

    with pytest.raises(InvalidVerificationCode):
        await uc.execute(
            dto=ResetPasswordRequest(
                email=Email("player@example.com"),
                verification_code="123456",
                new_password="newpass",
            )
        )

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_reset_password_fails_when_code_wrong(mock_uow: UnitOfWork, mocker):
    mock_uow.verification_codes.get_code = AsyncMock(return_value="654321")
    hasher = mocker.MagicMock(spec=StringHasher)
    uc = ResetPasswordUseCase(uow=mock_uow, hasher=hasher)

    with pytest.raises(InvalidVerificationCode):
        await uc.execute(
            dto=ResetPasswordRequest(
                email=Email("player@example.com"),
                verification_code="123456",
                new_password="newpass",
            )
        )

    mock_uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_reset_password_success_hashes_and_saves(mock_uow: UnitOfWork, fake_user: User, mocker):
    mock_uow.verification_codes.get_code = AsyncMock(return_value="123456")
    mock_uow.users.get_by_email = AsyncMock(return_value=fake_user)
    hasher = mocker.MagicMock(spec=StringHasher)
    hasher.hash.return_value = "new_hash"
    uc = ResetPasswordUseCase(uow=mock_uow, hasher=hasher)

    result = await uc.execute(
        dto=ResetPasswordRequest(
            email=Email("player@example.com"),
            verification_code="123456",
            new_password="newpass",
        )
    )

    assert result.ok is True
    assert fake_user.password_hash == "new_hash"
    hasher.hash.assert_called_once_with(raw="newpass")
    mock_uow.users.save.assert_awaited_once_with(user=fake_user)
    mock_uow.commit.assert_awaited_once()

from typing import Annotated

from fastapi import Depends

from application.use_cases.user.activate_user import ActivateUserUseCase
from application.use_cases.user.change_email import ChangeEmailUseCase
from application.use_cases.user.change_password import ChangePasswordUseCase
from application.use_cases.user.change_username import ChangeUsernameUseCase
from application.use_cases.user.get_login_history import GetLoginHistoryUseCase
from application.use_cases.user.me import MeUseCase
from application.use_cases.user.minecraft_profile.change_nickname import ChangeNicknameUseCase
from application.use_cases.user.send_verification_code import SendVerificationCodeUseCase
from domain.interfaces.services.code_generator import CodeGenerator
from domain.interfaces.services.email_service import EmailService
from domain.interfaces.services.string_hasher import StringHasher
from domain.interfaces.unit_of_work import UnitOfWork
from presentation.dependencies.services import get_code_generator, get_email_service, get_string_hasher
from presentation.dependencies.uow import get_uow

UOW = Annotated[UnitOfWork, Depends(get_uow)]
STRING_HASHER = Annotated[StringHasher, Depends(get_string_hasher)]
EMAIL_SERVICE = Annotated[EmailService, Depends(get_email_service)]
CODE_GENERATOR = Annotated[CodeGenerator, Depends(get_code_generator)]


def get_me_uc(uow: UOW) -> MeUseCase:
    return MeUseCase(uow=uow)


def get_activate_user_uc(uow: UOW) -> ActivateUserUseCase:
    return ActivateUserUseCase(uow=uow)


def get_send_verification_code_uc(
    uow: UOW,
    email_service: EMAIL_SERVICE,
    code_generator: CODE_GENERATOR,
) -> SendVerificationCodeUseCase:
    return SendVerificationCodeUseCase(uow=uow, email_service=email_service, code_generator=code_generator)


def get_change_email_uc(uow: UOW) -> ChangeEmailUseCase:
    return ChangeEmailUseCase(uow=uow)


def get_change_password_uc(uow: UOW, string_hasher: STRING_HASHER) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(uow=uow, hasher=string_hasher)


def get_change_username_uc(uow: UOW) -> ChangeUsernameUseCase:
    return ChangeUsernameUseCase(uow=uow)


def get_change_nickname_uc(uow: UOW) -> ChangeNicknameUseCase:
    return ChangeNicknameUseCase(uow=uow)


def get_login_history_uc(uow: UOW) -> GetLoginHistoryUseCase:
    return GetLoginHistoryUseCase(uow=uow)

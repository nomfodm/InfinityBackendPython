from typing import Annotated

from fastapi import Depends

from application.use_cases.admin.ban_user import BanUserUseCase
from application.use_cases.admin.force_logout_user import ForceLogoutUserUseCase
from application.use_cases.admin.get_user_login_history import GetUserLoginHistoryUseCase
from application.use_cases.admin.get_users import GetUsersUseCase
from application.use_cases.admin.pardon_user import PardonUserUseCase
from domain.interfaces.unit_of_work import UnitOfWork
from presentation.dependencies.uow import get_uow

UOW = Annotated[UnitOfWork, Depends(get_uow)]


def get_get_users_uc(uow: UOW) -> GetUsersUseCase:
    return GetUsersUseCase(uow=uow)


def get_ban_user_uc(uow: UOW) -> BanUserUseCase:
    return BanUserUseCase(uow=uow)


def get_pardon_user_uc(uow: UOW) -> PardonUserUseCase:
    return PardonUserUseCase(uow=uow)


def get_force_logout_uc(uow: UOW) -> ForceLogoutUserUseCase:
    return ForceLogoutUserUseCase(uow=uow)


def get_user_login_history_uc(uow: UOW) -> GetUserLoginHistoryUseCase:
    return GetUserLoginHistoryUseCase(uow=uow)

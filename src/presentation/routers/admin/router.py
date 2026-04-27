from typing import Annotated

from fastapi import APIRouter, Depends

from application.dtos.common import StatusResponse
from application.dtos.login_history import LoginHistoryEntryResponse
from application.use_cases.admin.ban_user import BanUserRequest, BanUserUseCase
from application.use_cases.admin.force_logout_user import ForceLogoutUserRequest, ForceLogoutUserUseCase
from application.use_cases.admin.get_user_login_history import GetUserLoginHistoryRequest, GetUserLoginHistoryUseCase
from application.use_cases.admin.get_users import AdminUserResponse, GetUsersUseCase
from application.use_cases.admin.pardon_user import PardonUserRequest, PardonUserUseCase
from presentation.dependencies.auth import CURRENT_USER
from presentation.routers.admin.dependencies import (
    get_ban_user_uc,
    get_force_logout_uc,
    get_get_users_uc,
    get_pardon_user_uc,
    get_user_login_history_uc,
)
from presentation.routers.admin.schemas import BanUserRequest as BanUserSchema

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get("/users", response_model=list[AdminUserResponse])
async def get_users(
    user: CURRENT_USER,
    uc: Annotated[GetUsersUseCase, Depends(get_get_users_uc)],
):
    return await uc.execute(user=user)


@admin_router.get("/users/{user_id}/login-history", response_model=list[LoginHistoryEntryResponse])
async def get_user_login_history(
    user_id: int,
    user: CURRENT_USER,
    uc: Annotated[GetUserLoginHistoryUseCase, Depends(get_user_login_history_uc)],
):
    return await uc.execute(dto=GetUserLoginHistoryRequest(user_id=user_id), user=user)


@admin_router.post("/users/{user_id}/ban", response_model=StatusResponse)
async def ban_user(
    user_id: int,
    data: BanUserSchema,
    user: CURRENT_USER,
    uc: Annotated[BanUserUseCase, Depends(get_ban_user_uc)],
):
    return await uc.execute(
        dto=BanUserRequest(
            user_id=user_id,
            ban_type=data.ban_type,
            banned_till=data.banned_till,
        ),
        user=user,
    )


@admin_router.post("/users/{user_id}/pardon", response_model=StatusResponse)
async def pardon_user(
    user_id: int,
    user: CURRENT_USER,
    uc: Annotated[PardonUserUseCase, Depends(get_pardon_user_uc)],
):
    return await uc.execute(dto=PardonUserRequest(user_id=user_id), user=user)


@admin_router.post("/users/{user_id}/force-logout", response_model=StatusResponse)
async def force_logout(
    user_id: int,
    user: CURRENT_USER,
    uc: Annotated[ForceLogoutUserUseCase, Depends(get_force_logout_uc)],
):
    return await uc.execute(dto=ForceLogoutUserRequest(user_id=user_id), user=user)

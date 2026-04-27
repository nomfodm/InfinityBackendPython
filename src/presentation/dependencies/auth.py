from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.entities.user import User
from domain.exceptions.user import UserNotFoundError
from domain.interfaces.services.token_service import TokenService
from domain.interfaces.unit_of_work import UnitOfWork
from presentation.dependencies.services import get_token_service
from presentation.dependencies.uow import get_uow

_http_bearer = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_http_bearer)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> User:
    payload = token_service.decode_access_token(token=credentials.credentials)
    user_id = int(payload["sub"])
    async with uow:
        user = await uow.users.get_by_id(id=user_id)
    if user is None:
        raise UserNotFoundError("Пользователь не найден.")
    return user


CURRENT_USER = Annotated[User, Depends(get_current_user)]

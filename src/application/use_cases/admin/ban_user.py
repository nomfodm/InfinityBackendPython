import datetime
from dataclasses import dataclass
from enum import StrEnum

from application.decorators.auth import require_login, roles_allowed
from application.dtos.common import StatusResponse
from domain.entities.user import Role, User
from domain.exceptions.base import ValidationError
from domain.exceptions.user import UserNotFoundError
from domain.interfaces.unit_of_work import UnitOfWork


class BanType(StrEnum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"


@dataclass(frozen=True)
class BanUserRequest:
    ban_type: BanType
    user_to_ban_id: int
    banned_till: datetime.datetime | None = None

    def __post_init__(self) -> None:
        if self.ban_type == BanType.TEMPORARY and self.banned_till is None:
            raise ValidationError("Для временной блокировки необходимо указать дату окончания.")


class BanUserUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @roles_allowed(Role.ADMIN)
    async def execute(self, *, dto: BanUserRequest, user: User) -> StatusResponse:
        async with self._uow:
            user_to_ban = await self._uow.users.get_by_id(id=dto.user_to_ban_id)
            if user_to_ban is None:
                raise UserNotFoundError("Пользователь не найден.")

            user_to_ban.ban_status.is_banned = True
            user_to_ban.ban_status.admin_user_id = user.id
            if dto.ban_type == BanType.PERMANENT:
                user_to_ban.ban_status.is_permanent = True
            elif dto.ban_type == BanType.TEMPORARY:
                user_to_ban.ban_status.banned_till = dto.banned_till

            await self._uow.users.save(user=user_to_ban)

            await self._uow.commit()
            return StatusResponse()

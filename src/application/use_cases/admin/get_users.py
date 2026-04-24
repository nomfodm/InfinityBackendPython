import datetime
from dataclasses import dataclass

from application.decorators.auth import require_login, require_not_banned, roles_allowed
from application.dtos.user import BanStatusResponse
from domain.entities.user import Role, User
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class AdminUserResponse:
    id: int
    email: str
    username: str
    roles: list[str]
    ban_status: BanStatusResponse
    is_active: bool
    registered_at: datetime.datetime

    @classmethod
    def from_domain(cls, user: User):
        return cls(
            id=user.id,
            email=user.email.value,
            username=user.username.value,
            roles=list(user.roles),
            ban_status=BanStatusResponse(
                is_banned=user.ban_status.is_banned,
                is_permanent=user.ban_status.is_permanent,
                banned_till=user.ban_status.banned_till,
                admin_user_id=user.ban_status.admin_user_id,
            ),
            is_active=user.is_active,
            registered_at=user.registered_at,
        )


class GetUsersUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    @require_not_banned
    @roles_allowed(Role.ADMIN)
    async def execute(self, *, user: User) -> list[AdminUserResponse]:
        async with self._uow:
            users = await self._uow.users.get_all()
            return [AdminUserResponse.from_domain(u) for u in users]

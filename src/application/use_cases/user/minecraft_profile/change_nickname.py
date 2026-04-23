from dataclasses import dataclass

from application.decorators.auth import require_login
from application.dtos.common import StatusResponse
from domain.entities.user import User
from domain.entities.base import UserRelatedHandle
from domain.exceptions.user import NicknameTakenError
from domain.interfaces.unit_of_work import UnitOfWork

@dataclass(frozen=True)
class ChangeNicknameRequest:
    new_nickname: UserRelatedHandle


class ChangeNicknameUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    async def execute(self, *, dto: ChangeNicknameRequest, user: User) -> StatusResponse:
        async with self._uow:
            existing_nickname = await self._uow.minecraft_profiles.get_by_nickname(nickname=dto.new_nickname)
            if existing_nickname and existing_nickname.user_id != user.id:
                raise NicknameTakenError("Этот никнейм занят.")

            mc_profile = await self._uow.minecraft_profiles.get_by_user_id_or_raise(user_id=user.id)
            mc_profile.nickname = dto.new_nickname

            await self._uow.minecraft_profiles.save(profile=mc_profile)

            await self._uow.commit()
            return StatusResponse()

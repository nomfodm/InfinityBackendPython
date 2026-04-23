from application.decorators.auth import require_login
from application.dtos.minecraft_session import MinecraftSessionResponse
from domain.entities.minecraft_session import MinecraftSession
from domain.entities.user import User
from domain.interfaces.unit_of_work import UnitOfWork
from domain.utils.crypto import generate_token_32_length


class CreateMinecraftSessionUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    @require_login
    async def execute(self, *, user: User) -> MinecraftSessionResponse:
        async with self._uow:
            mc_profile = await self._uow.minecraft_profiles.get_by_user_id_or_raise(user_id=user.id)

            new_mc_session = await self._uow.minecraft_sessions.save(
                mc_session=MinecraftSession(
                    user_id=user.id,
                    profile_uuid=mc_profile.uuid,
                    nickname=mc_profile.nickname,
                    access_token=generate_token_32_length(),
                )
            )
            await self._uow.commit()

            return MinecraftSessionResponse(
                access_token=new_mc_session.access_token.value,
                profile_uuid=str(mc_profile.uuid),
                nickname=mc_profile.nickname.value,
            )

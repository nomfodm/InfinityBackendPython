import uuid
from dataclasses import dataclass

from application.constants import MC_SESSION_TTL_SECONDS
from application.dtos.common import StatusResponse
from domain.entities.base import MCAccessToken, MCServerID
from domain.exceptions.minecraft import InvalidMCAccessToken
from domain.interfaces.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class JoinServerRequest:
    access_token: MCAccessToken
    selected_profile: uuid.UUID
    server_id: MCServerID


class JoinServerUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, *, dto: JoinServerRequest) -> StatusResponse:
        async with self._uow:
            mc_session = await self._uow.minecraft_sessions.get_by_profile_uuid_or_raise(
                profile_uuid=dto.selected_profile
            )

            if mc_session.access_token != dto.access_token:
                raise InvalidMCAccessToken("Неверный токен доступа.")

            mc_session.server_id = dto.server_id

            await self._uow.minecraft_sessions.save(mc_session=mc_session, ttl=MC_SESSION_TTL_SECONDS)

            await self._uow.commit()
            return StatusResponse()

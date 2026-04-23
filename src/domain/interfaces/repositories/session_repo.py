import uuid
from typing import Protocol

from domain.entities.session import Session
from domain.exceptions.session import SessionNotFoundError


class SessionRepository(Protocol):
    async def save(self, *, session: Session) -> Session:
        pass

    async def get_by_id(self, *, uuid: uuid.UUID) -> Session | None:
        pass

    async def get_by_id_or_raise(self, *, uuid: uuid.UUID) -> Session:
        session = await self.get_by_id(uuid=uuid)
        if session is None:
            raise SessionNotFoundError("Сессия не найдена.")
        return session

    async def delete(self, *, session: Session) -> None:
        pass

    async def delete_others_by_user_id(self, *, user_id: int, exclude_session_id: uuid.UUID) -> None:
        pass

    async def delete_invalid_by_user_id(self, *, user_id: int) -> None:
        pass

    async def get_all_by_user_id(self, *, user_id: int) -> list[Session]:
        pass

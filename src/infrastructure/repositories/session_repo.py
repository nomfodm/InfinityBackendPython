import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.session import Session
from domain.exceptions.session import SessionNotFoundError
from domain.interfaces.repositories.session_repo import SessionRepository
from infrastructure.database.models.session_model import SessionModel


class SqlSessionRepository(SessionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, session: Session) -> Session:
        merged = await self._session.merge(SessionModel.from_domain(session))
        await self._session.flush()
        return merged.to_domain()

    async def get_by_id(self, uuid: uuid.UUID) -> Session | None:
        result = await self._session.execute(select(SessionModel).where(SessionModel.id == uuid))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_id_or_raise(self, uuid: uuid.UUID) -> Session:
        session = await self.get_by_id(uuid)
        if session is None:
            raise SessionNotFoundError("Сессия не найдена.")
        return session

    async def delete(self, session: Session) -> None:
        await self._session.execute(delete(SessionModel).where(SessionModel.id == session.id))

    async def delete_others_by_user_id(self, user_id: int, exclude_session_id: uuid.UUID) -> None:
        await self._session.execute(
            delete(SessionModel).where(
                SessionModel.user_id == user_id,
                SessionModel.id != exclude_session_id,
            )
        )

    async def delete_invalid_by_user_id(self, user_id: int) -> None:
        await self._session.execute(
            delete(SessionModel).where(
                SessionModel.user_id == user_id,
                or_(
                    SessionModel.is_revoked == True,  # noqa: E712
                    SessionModel.expires_at < datetime.now(UTC),
                ),
            )
        )

    async def get_all_by_user_id(self, user_id: int) -> list[Session]:
        result = await self._session.execute(select(SessionModel).where(SessionModel.user_id == user_id))
        return [m.to_domain() for m in result.scalars().all()]

    async def delete_all_by_user_id(self, user_id: int) -> None:
        await self._session.execute(delete(SessionModel).where(SessionModel.user_id == user_id))

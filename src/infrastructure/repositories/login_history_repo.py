from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.login_history import LoginHistoryEntry
from domain.interfaces.repositories.login_history_repo import LoginHistoryRepository
from infrastructure.database.models.login_history_model import LoginHistoryEntryModel


class SqlLoginHistoryRepository(LoginHistoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, entry: LoginHistoryEntry) -> None:
        self._session.add(LoginHistoryEntryModel.from_domain(entry))
        await self._session.flush()

    async def get_by_user_id(self, user_id: int) -> list[LoginHistoryEntry]:
        result = await self._session.execute(
            select(LoginHistoryEntryModel)
            .where(LoginHistoryEntryModel.user_id == user_id)
            .order_by(LoginHistoryEntryModel.timestamp.desc())
        )
        return [m.to_domain() for m in result.scalars().all()]

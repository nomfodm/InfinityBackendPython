from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import User
from domain.interfaces.repositories.user_repo import UserRepository
from infrastructure.database.models.user_model import UserModel


class SqlUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> User:
        merged = await self._session.merge(UserModel.from_domain(user))
        await self._session.flush()
        return merged.to_domain()

    async def get_by_username(self, username: UserRelatedHandle) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.username == username.value))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_email(self, email: Email) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email.value))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_id(self, id: int) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_all(self) -> list[User]:
        result = await self._session.execute(select(UserModel))
        return [m.to_domain() for m in result.scalars().all()]

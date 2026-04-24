from typing import Protocol

from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import User


class UserRepository(Protocol):
    async def save(self, *, user: User) -> User:
        pass

    async def get_by_username(self, *, username: UserRelatedHandle) -> User | None:
        pass

    async def get_by_email(self, *, email: Email) -> User | None:
        pass

    async def get_by_id(self, *, id: int) -> User | None:
        pass

    async def get_all(self) -> list[User]:
        pass

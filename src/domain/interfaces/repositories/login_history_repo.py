from typing import Protocol

from domain.entities.login_history import LoginHistoryEntry


class LoginHistoryRepository(Protocol):
    async def save(self, *, entry: LoginHistoryEntry) -> None:
        pass

    async def get_by_user_id(self, *, user_id: int) -> list[LoginHistoryEntry]:
        pass

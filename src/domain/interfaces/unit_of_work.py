from typing import Protocol

from domain.interfaces.repositories.launcher_release_repo import LauncherReleaseRepository
from domain.interfaces.repositories.login_history_repo import LoginHistoryRepository
from domain.interfaces.repositories.minecraft_profile_repo import MinecraftProfileRepository
from domain.interfaces.repositories.minecraft_session_repo import MinecraftSessionRepository
from domain.interfaces.repositories.session_repo import SessionRepository
from domain.interfaces.repositories.texture_catalog_repo import TextureCatalogRepository
from domain.interfaces.repositories.texture_repo import TextureRepository
from domain.interfaces.repositories.user_repo import UserRepository
from domain.interfaces.repositories.verification_code_repo import VerificationCodeRepository
from domain.interfaces.repositories.wardrobe_item_repo import WardrobeItemRepository


class UnitOfWork(Protocol):
    users: UserRepository
    verification_codes: VerificationCodeRepository  # redis
    minecraft_profiles: MinecraftProfileRepository
    minecraft_sessions: MinecraftSessionRepository  # redis
    wardrobe: WardrobeItemRepository
    textures: TextureRepository
    texture_catalog: TextureCatalogRepository
    sessions: SessionRepository
    login_histories: LoginHistoryRepository
    launcher_releases: LauncherReleaseRepository

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.rollback()

    async def commit(self):
        pass

    async def rollback(self):
        pass

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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
from infrastructure.redis.minecraft_session_repo import RedisMinecraftSessionRepository
from infrastructure.redis.verification_code_repo import RedisVerificationCodeRepository
from infrastructure.repositories.launcher_release_repo import SqlLauncherReleaseRepository
from infrastructure.repositories.login_history_repo import SqlLoginHistoryRepository
from infrastructure.repositories.minecraft_profile_repo import SqlMinecraftProfileRepository
from infrastructure.repositories.session_repo import SqlSessionRepository
from infrastructure.repositories.texture_catalog_repo import SqlTextureCatalogRepository
from infrastructure.repositories.texture_repo import SqlTextureRepository
from infrastructure.repositories.user_repo import SqlUserRepository
from infrastructure.repositories.wardrobe_item_repo import SqlWardrobeItemRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, *, session_factory: async_sessionmaker[AsyncSession], redis: Redis) -> None:
        self._session_factory = session_factory
        self._redis = redis

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session: AsyncSession = self._session_factory()
        self._cache: dict = {}
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    @property
    def users(self) -> UserRepository:
        if "users" not in self._cache:
            self._cache["users"] = SqlUserRepository(self._session)
        return self._cache["users"]

    @property
    def sessions(self) -> SessionRepository:
        if "sessions" not in self._cache:
            self._cache["sessions"] = SqlSessionRepository(self._session)
        return self._cache["sessions"]

    @property
    def minecraft_profiles(self) -> MinecraftProfileRepository:
        if "minecraft_profiles" not in self._cache:
            self._cache["minecraft_profiles"] = SqlMinecraftProfileRepository(self._session)
        return self._cache["minecraft_profiles"]

    @property
    def wardrobe(self) -> WardrobeItemRepository:
        if "wardrobe" not in self._cache:
            self._cache["wardrobe"] = SqlWardrobeItemRepository(self._session)
        return self._cache["wardrobe"]

    @property
    def textures(self) -> TextureRepository:
        if "textures" not in self._cache:
            self._cache["textures"] = SqlTextureRepository(self._session)
        return self._cache["textures"]

    @property
    def texture_catalog(self) -> TextureCatalogRepository:
        if "texture_catalog" not in self._cache:
            self._cache["texture_catalog"] = SqlTextureCatalogRepository(self._session)
        return self._cache["texture_catalog"]

    @property
    def launcher_releases(self) -> LauncherReleaseRepository:
        if "launcher_releases" not in self._cache:
            self._cache["launcher_releases"] = SqlLauncherReleaseRepository(self._session)
        return self._cache["launcher_releases"]

    @property
    def login_histories(self) -> LoginHistoryRepository:
        if "login_histories" not in self._cache:
            self._cache["login_histories"] = SqlLoginHistoryRepository(self._session)
        return self._cache["login_histories"]

    @property
    def verification_codes(self) -> VerificationCodeRepository:
        if "verification_codes" not in self._cache:
            self._cache["verification_codes"] = RedisVerificationCodeRepository(self._redis)
        return self._cache["verification_codes"]

    @property
    def minecraft_sessions(self) -> MinecraftSessionRepository:
        if "minecraft_sessions" not in self._cache:
            self._cache["minecraft_sessions"] = RedisMinecraftSessionRepository(self._redis)
        return self._cache["minecraft_sessions"]

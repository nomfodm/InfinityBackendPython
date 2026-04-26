from infrastructure.database.models.base import Base
from infrastructure.database.models.launcher_model import LauncherReleaseAssetModel, LauncherReleaseModel  # noqa: F401
from infrastructure.database.models.login_history_model import LoginHistoryEntryModel  # noqa: F401
from infrastructure.database.models.minecraft_profile_model import MinecraftProfileModel  # noqa: F401
from infrastructure.database.models.session_model import SessionModel  # noqa: F401
from infrastructure.database.models.user_model import UserModel  # noqa: F401
from infrastructure.database.models.wardrobe_model import (  # noqa: F401
    TextureCatalogItemModel,
    TextureModel,
    WardrobeItemModel,
)
from infrastructure.database.session import engine


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

import asyncio
from datetime import UTC, datetime

import pytest
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import User
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
from infrastructure.repositories.user_repo import SqlUserRepository


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def test_engine(postgres_container):
    url = (
        f"postgresql+asyncpg://{postgres_container.username}:{postgres_container.password}"
        f"@{postgres_container.get_container_host_ip()}"
        f":{postgres_container.get_exposed_port(5432)}/{postgres_container.dbname}"
    )
    engine = create_async_engine(url, poolclass=NullPool)

    async def _create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_create_tables())
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture
async def db_session(test_engine) -> AsyncSession:
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def saved_user(db_session) -> User:
    return await SqlUserRepository(db_session).save(
        User(
            email=Email("base@test.com"),
            username=UserRelatedHandle("baseuser"),
            password_hash="hash",
            registered_at=datetime.now(UTC),
        )
    )


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as r:
        yield r


@pytest.fixture
async def redis_client(redis_container):
    client = aioredis.Redis(
        host=redis_container.get_container_host_ip(),
        port=int(redis_container.get_exposed_port(6379)),
        decode_responses=True,
    )
    yield client
    await client.flushdb()
    await client.aclose()

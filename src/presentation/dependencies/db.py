from functools import lru_cache

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.config import settings
from infrastructure.database.session import AsyncSessionLocal


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return AsyncSessionLocal


@lru_cache
def get_redis_client() -> Redis:
    return Redis(host=settings.redis.host, port=settings.redis.port, db=settings.redis.db, decode_responses=True)

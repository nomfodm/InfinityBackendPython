from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from presentation.dependencies.db import get_redis_client, get_session_factory


async def get_uow(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory=session, redis=redis_client)

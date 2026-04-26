from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from infrastructure.config import settings

engine = create_async_engine(str(settings.database.url), echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

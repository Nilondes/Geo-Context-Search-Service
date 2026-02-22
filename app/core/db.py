import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://geo:geo_password@localhost:5433/geo_search",
)


engine = create_async_engine(
    DATABASE_URL,
    # Keep SQL echo on for local debugging; switch off in production envs.
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    # Avoid invalidating ORM objects after commit; useful for read-after-write flows.
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session():
    # FastAPI dependency that scopes a session to the request lifecycle.
    async with AsyncSessionLocal() as session:
        yield session

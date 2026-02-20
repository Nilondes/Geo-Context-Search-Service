import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.models.base import Base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://geo:geo_password@localhost:5433/geo_search",
)


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

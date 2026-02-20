from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.base import Base

DATABASE_URL = "postgresql+asyncpg://geo:geo_password@localhost:5433/geo_search"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

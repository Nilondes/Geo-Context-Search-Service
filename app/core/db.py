import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.env import load_env


load_env()


def _build_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    if all([host, port, name, user, password]):
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
    raise RuntimeError("DATABASE_URL or DB_* environment variables must be set")


_engine = None
_sessionmaker = None


def _get_engine():
    global _engine, _sessionmaker
    if _engine is None:
        database_url = _build_database_url()
        _engine = create_async_engine(
            database_url,
            # Keep SQL echo on for local debugging; switch off in production envs.
            echo=True,
        )
        _sessionmaker = async_sessionmaker(
            bind=_engine,
            # Avoid invalidating ORM objects after commit; useful for read-after-write flows.
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _engine, _sessionmaker


async def get_session():
    # FastAPI dependency that scopes a session to the request lifecycle.
    _, sessionmaker = _get_engine()
    async with sessionmaker() as session:
        yield session

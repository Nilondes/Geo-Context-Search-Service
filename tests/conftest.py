import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.main import app
from app.core.db import get_session
from app.core.env import load_env

load_env()

def _build_test_database_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if url:
        return url
    host = os.getenv("TEST_DB_HOST")
    port = os.getenv("TEST_DB_PORT")
    name = os.getenv("TEST_DB_NAME")
    user = os.getenv("TEST_DB_USER")
    password = os.getenv("TEST_DB_PASSWORD")
    if all([host, port, name, user, password]):
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
    raise RuntimeError("TEST_DATABASE_URL or TEST_DB_* environment variables must be set")


TEST_DATABASE_URL = _build_test_database_url()


@pytest.fixture
async def engine():
    """Create a fresh engine for each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Create a new database session for each test."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Create an async HTTP client for testing."""

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

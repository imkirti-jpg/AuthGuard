from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession , async_sessionmaker
from sqlalchemy.orm import sessionmaker
from redis.asyncio import Redis
from fastapi.testclient import TestClient
from app.core.seed_roles import seed_roles
from app.db.session import get_db
from app.main import app
from app.db.base import Base
from unittest.mock import AsyncMock, patch
import sys

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/testdb"


# Mock Redis client for all tests
class MockRedis:
    def __init__(self):
        self.data = {}
    
    async def set(self, key, value, ex=None):
        self.data[key] = value
        return True
    
    async def get(self, key):
        return self.data.get(key)
    
    async def delete(self, key):
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    async def ping(self):
        return True
    
    async def flushdb(self):
        self.data.clear()
    
    async def aclose(self):
        pass


@pytest.fixture(scope="function", autouse=True)
async def mock_redis():
    """Automatically mock Redis for all tests"""
    mock_redis_client = MockRedis()
    with patch('app.db.redis.get_redis_client') as mock_get_redis:
        mock_get_redis.return_value = mock_redis_client
        yield mock_redis_client


@pytest.fixture(scope="function")
async def async_db_session():
    engine = create_async_engine(DATABASE_URL, future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed roles into the fresh test database
    async with async_session() as session:
        await seed_roles(session) 
        
    async with async_session() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def redis_client():
    client = Redis(
        host="localhost",
        port=6379,
        db=1,
        decode_responses=True,
    )

    await client.ping()   # force connection on active loop
    await client.flushdb()

    yield client

    await client.flushdb()
    await client.aclose() 

@pytest.fixture(scope="function")
async def client(async_db_session):
    # Override dependency to use the test session
    async def _get_test_db():
        yield async_db_session
    
    app.dependency_overrides[get_db] = _get_test_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()